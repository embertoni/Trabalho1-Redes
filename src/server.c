/* Habilita as declarações POSIX usadas por sockets, arquivos e threads */
#define _POSIX_C_SOURCE 200809L

/* Contrato compartilhado: parser, respostas, limites e envio completo */
#include "protocol.h"

/* APIs do sistema e da biblioteca C para rede, disco e tratamento de erros */
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <inttypes.h>
#include <limits.h>
#include <netdb.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

/* Fila de conexões pendentes e capacidades dos buffers locais */
#define SERVER_BACKLOG 128
#define SERVER_RESPONSE_BUFFER 512
#define SERVER_TRANSFER_BUFFER (64U * 1024U)

/* Impede seguir o link simbólico final no GET/HEAD quando houver suporte */
#if defined(O_NOFOLLOW)
#define SERVER_OPEN_FLAGS O_RDONLY | O_NOFOLLOW
#else
#define SERVER_OPEN_FLAGS O_RDONLY
#endif

/* Estado exclusivo de cada conexão; a thread assume sua liberação */
typedef struct {
    int client_fd;
    char root[PATH_MAX];
    protocol_limits_t limits;
} client_context_t;

/* Flag acessada pelo handler de sinal e pelo laço de aceitação */
static volatile sig_atomic_t server_running = 1;

/* Sinaliza o pedido de parada sem executar limpeza dentro do handler */
static void handle_signal(int signal_number)
{
    (void)signal_number;
    server_running = 0;
}

/* Exibe em stderr as opções públicas da linha de comando */
static void print_usage(const char *program)
{
    fprintf(
        stderr,
        "Uso: %s [opcoes]\n"
        "\n"
        "Opcoes:\n"
        "  --host ENDERECO          endereco de escuta (padrao: %s)\n"
        "  --port PORTA             porta TCP (padrao: %d)\n"
        "  --root DIRETORIO         raiz de arquivos (padrao: %s)\n"
        "  --max-file-size BYTES    tamanho maximo de arquivo\n"
        "  --help                   mostra esta ajuda\n",
        program,
        PROTOCOL_DEFAULT_HOST,
        PROTOCOL_DEFAULT_PORT,
        PROTOCOL_DEFAULT_ROOT
    );
}

/* Converte a porta e verifica conversão completa e faixa de 1 a 65535 */
static int parse_port(const char *text, uint16_t *port)
{
    char *end = NULL;
    unsigned long value;

    if (text == NULL || text[0] == '\0') {
        return 0;
    }

    errno = 0;
    value = strtoul(text, &end, 10);

    if (errno != 0 || end == text || *end != '\0' ||
        value == 0 || value > 65535UL) {
        return 0;
    }

    *port = (uint16_t)value;
    return 1;
}

/* Converte o limite numérico e verifica erros e caracteres restantes */
static int parse_u64(const char *text, uint64_t *value)
{
    char *end = NULL;
    unsigned long long parsed;

    if (text == NULL || text[0] == '\0') {
        return 0;
    }

    errno = 0;
    parsed = strtoull(text, &end, 10);

    if (errno != 0 || end == text || *end != '\0') {
        return 0;
    }

    *value = (uint64_t)parsed;
    return 1;
}

/* Resolve o endereço, associa um socket TCP e o coloca em escuta */
static int create_listener(const char *host, uint16_t port)
{
    struct addrinfo hints;
    struct addrinfo *results = NULL;
    struct addrinfo *current;
    char port_text[16];
    int listener_fd = -1;
    int enable_reuse = 1;
    int result;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    if (snprintf(port_text, sizeof(port_text), "%u", (unsigned)port) < 0) {
        return -1;
    }

    result = getaddrinfo(host, port_text, &hints, &results);

    if (result != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(result));
        return -1;
    }

    /* Tenta os endereços resolvidos até conseguir realizar bind */
    for (current = results; current != NULL; current = current->ai_next) {
        listener_fd = socket(
            current->ai_family,
            current->ai_socktype,
            current->ai_protocol
        );

        if (listener_fd < 0) {
            continue;
        }

        /* Permite reutilizar o endereço local ao reiniciar o servidor */
        if (setsockopt(
                listener_fd,
                SOL_SOCKET,
                SO_REUSEADDR,
                &enable_reuse,
                sizeof(enable_reuse)
            ) < 0) {
            close(listener_fd);
            listener_fd = -1;
            continue;
        }

        if (bind(
                listener_fd,
                current->ai_addr,
                current->ai_addrlen
            ) == 0) {
            break;
        }

        close(listener_fd);
        listener_fd = -1;
    }

    freeaddrinfo(results);

    if (listener_fd < 0) {
        perror("bind");
        return -1;
    }

    if (listen(listener_fd, SERVER_BACKLOG) < 0) {
        perror("listen");
        close(listener_fd);
        return -1;
    }

    return listener_fd;
}

/* Monta e envia uma resposta de status sem corpo */
static int send_status(int client_fd, int status_code)
{
    char response[SERVER_RESPONSE_BUFFER];
    int response_length;

    response_length = protocol_build_response(
        response,
        sizeof(response),
        status_code,
        0
    );

    if (response_length < 0) {
        return -1;
    }

    return protocol_send_all(
        client_fd,
        response,
        (size_t)response_length
    ) == (ssize_t)response_length ? 0 : -1;
}

/* Valida o nome remoto e o combina com a raiz, removendo a barra inicial */
static int build_local_path(const char *root, const char *remote_path, char *output, size_t output_capacity)
{
    int written;

    if (root == NULL || remote_path == NULL || output == NULL) {
        return -1;
    }

    if (!protocol_validate_path(
            remote_path,
            PROTOCOL_MAX_PATH_LEN
        )) {
        return -1;
    }

    written = snprintf(
        output,
        output_capacity,
        "%s/%s",
        root,
        remote_path + 1
    );

    if (written < 0 || (size_t)written >= output_capacity) {
        return -1;
    }

    return 0;
}

/* Envia o comprimento indicado em blocos, tratando leitura interrompida */
static int send_file_contents(int client_fd, int file_fd, uint64_t length)
{
    unsigned char buffer[SERVER_TRANSFER_BUFFER];
    uint64_t remaining = length;

    while (remaining > 0) {
        size_t requested = sizeof(buffer);
        ssize_t bytes_read;

        if (remaining < (uint64_t)requested) {
            requested = (size_t)remaining;
        }

        do {
            bytes_read = read(file_fd, buffer, requested);
        } while (bytes_read < 0 && errno == EINTR);

        if (bytes_read <= 0) {
            return -1;
        }

        /* O helper completa o envio mesmo quando send transfere menos bytes */
        if (protocol_send_all(
                client_fd,
                buffer,
                (size_t)bytes_read
            ) != bytes_read) {
            return -1;
        }

        remaining -= (uint64_t)bytes_read;
    }

    return 0;
}

/* Abre e verifica o arquivo; GET envia o conteúdo e HEAD apenas a resposta */
static int handle_get_or_head(const client_context_t *context, const protocol_request_t *request)
{
    char local_path[PATH_MAX];
    struct stat file_stat;
    char response[SERVER_RESPONSE_BUFFER];
    int response_length;
    int file_fd;
    int result;

    if (build_local_path(
            context->root,
            request->path,
            local_path,
            sizeof(local_path)
        ) < 0) {
        return send_status(context->client_fd, STATUS_BAD_REQUEST);
    }

    /* A abertura usa a proteção contra link simbólico definida acima */
    file_fd = open(local_path, SERVER_OPEN_FLAGS);

    if (file_fd < 0) {
        if (errno == ENOENT || errno == ENOTDIR || errno == ELOOP) {
            return send_status(context->client_fd, STATUS_NOT_FOUND);
        }

        perror("open GET/HEAD");
        return send_status(
            context->client_fd,
            STATUS_INTERNAL_SERVER_ERROR
        );
    }

    /* Consulta o arquivo já aberto e aceita somente arquivo regular no limite */
    if (fstat(file_fd, &file_stat) < 0) {
        perror("fstat");
        close(file_fd);
        return send_status(
            context->client_fd,
            STATUS_INTERNAL_SERVER_ERROR
        );
    }

    if (!S_ISREG(file_stat.st_mode) || file_stat.st_size < 0) {
        close(file_fd);
        return send_status(context->client_fd, STATUS_NOT_FOUND);
    }

    if ((uint64_t)file_stat.st_size > context->limits.max_file_size) {
        close(file_fd);
        return send_status(
            context->client_fd,
            STATUS_CONTENT_TOO_LARGE
        );
    }

    response_length = protocol_build_response(
        response,
        sizeof(response),
        STATUS_OK,
        /* Nesta implementação, HEAD anuncia comprimento zero e não envia corpo */
        request->method == METHOD_HEAD ? 0 : (uint64_t)file_stat.st_size
    );

    if (response_length < 0) {
        close(file_fd);
        return -1;
    }

    if (protocol_send_all(
            context->client_fd,
            response,
            (size_t)response_length
        ) != (ssize_t)response_length) {
        close(file_fd);
        return -1;
    }

    if (request->method == METHOD_HEAD) {
        close(file_fd);
        return 0;
    }

    /* Depois do cabeçalho, falhas no corpo encerram a transferência */
    result = send_file_contents(
        context->client_fd,
        file_fd,
        (uint64_t)file_stat.st_size
    );

    close(file_fd);
    return result;
}

/* Recebe exatamente o tamanho declarado e grava cada bloco por completo */
static int receive_exact_to_file(int client_fd, int file_fd, uint64_t length)
{
    unsigned char buffer[SERVER_TRANSFER_BUFFER];
    uint64_t remaining = length;

    while (remaining > 0) {
        size_t requested = sizeof(buffer);
        ssize_t bytes_received;

        if (remaining < (uint64_t)requested) {
            requested = (size_t)remaining;
        }

        /* Limita recv ao restante do corpo e repete em caso de EINTR */
        do {
            bytes_received = recv(
                client_fd,
                buffer,
                requested,
                0
            );
        } while (bytes_received < 0 && errno == EINTR);

        if (bytes_received <= 0) {
            return -1;
        }

        {
            size_t written = 0;

            /* write pode consumir apenas parte do bloco recebido */
            while (written < (size_t)bytes_received) {
                ssize_t bytes_written;

                do {
                    bytes_written = write(
                        file_fd,
                        buffer + written,
                        (size_t)bytes_received - written
                    );
                } while (bytes_written < 0 && errno == EINTR);

                if (bytes_written <= 0) {
                    return -1;
                }

                written += (size_t)bytes_written;
            }
        }

        remaining -= (uint64_t)bytes_received;
    }

    return 0;
}

/* Recebe PUT em temporário e publica o arquivo antes de confirmar sucesso */
static int handle_put(const client_context_t *context, const protocol_request_t *request)
{
    char local_path[PATH_MAX];
    char temporary_template[PATH_MAX];
    char response[SERVER_RESPONSE_BUFFER];
    struct stat existing_stat;
    int temporary_fd = -1;
    int response_length;
    int existed = 0;
    int result = -1;

    if (build_local_path(
            context->root,
            request->path,
            local_path,
            sizeof(local_path)
        ) < 0) {
        return send_status(context->client_fd, STATUS_BAD_REQUEST);
    }

    /* Registra a existência inicial para escolher entre 200 e 201 */
    if (stat(local_path, &existing_stat) == 0) {
        existed = 1;
    } else if (errno != ENOENT && errno != ENOTDIR) {
        perror("stat PUT");
        return send_status(
            context->client_fd,
            STATUS_INTERNAL_SERVER_ERROR
        );
    }

    if (snprintf(
            temporary_template,
            sizeof(temporary_template),
            "%s/.upload-XXXXXX",
            context->root
        ) < 0 || strlen(temporary_template) >= sizeof(temporary_template)) {
        return send_status(
            context->client_fd,
            STATUS_INSUFFICIENT_STORAGE
        );
    }

    /* Nome exclusivo por operação: threads compartilham PID, mas não temporário */
    temporary_fd = mkstemp(temporary_template);

    if (temporary_fd < 0) {
        perror("mkstemp");
        return send_status(
            context->client_fd,
            STATUS_INSUFFICIENT_STORAGE
        );
    }

    /* Define permissões e recebe o corpo sem truncar o destino anterior */
    if (fchmod(temporary_fd, 0644) < 0) {
        perror("fchmod");
        goto cleanup;
    }

    if (receive_exact_to_file(
            context->client_fd,
            temporary_fd,
            request->content_length
        ) < 0) {
        goto cleanup;
    }

    /* Sincroniza o conteúdo; não equivale a sincronizar o diretório publicado */
    if (fsync(temporary_fd) < 0) {
        perror("fsync");
        goto cleanup;
    }

    if (close(temporary_fd) < 0) {
        temporary_fd = -1;
        goto cleanup;
    }

    temporary_fd = -1;

    /* Publicação atômica na mesma raiz; a última publicação do nome prevalece */
    if (rename(temporary_template, local_path) < 0) {
        perror("rename PUT");
        goto cleanup;
    }

    response_length = protocol_build_response(
        response,
        sizeof(response),
        /* Confirma o PUT somente depois da publicação do arquivo completo */
        existed ? STATUS_OK : STATUS_CREATED,
        0
    );

    if (response_length < 0) {
        return -1;
    }

    result = protocol_send_all(
        context->client_fd,
        response,
        (size_t)response_length
    ) == (ssize_t)response_length ? 0 : -1;

/* Fecha o descritor pendente e remove o temporário em caso de falha */
cleanup:
    if (temporary_fd >= 0) {
        close(temporary_fd);
    }

    if (result != 0) {
        unlink(temporary_template);
    }

    return result;
}

/* Lê uma requisição, valida o cabeçalho, despacha o método e libera a conexão */
static void *client_thread(void *argument)
{
    client_context_t *context = argument;
    char header[PROTOCOL_MAX_HEADER_LEN + 1];
    ssize_t header_length;
    protocol_request_t request;
    protocol_result_t parse_result;

    if (context == NULL) {
        return NULL;
    }

    /* O helper recebe o cabeçalho até o delimitador, respeitando o buffer */
    header_length = protocol_recv_header(
        context->client_fd,
        header,
        sizeof(header)
    );

    if (header_length <= 0) {
        close(context->client_fd);
        free(context);
        return NULL;
    }

    /* O parser aplica os limites antes de iniciar a operação de arquivo */
    parse_result = protocol_parse_request(
        header,
        (size_t)header_length,
        0,
        &context->limits,
        &request
    );

    /* Converte falhas de parsing em status; metodos válidos seguem ao handler */
    if (parse_result == PROTOCOL_UNSUPPORTED) {
        (void)send_status(context->client_fd, STATUS_NOT_IMPLEMENTED);
    } else if (parse_result == PROTOCOL_TOO_LARGE) {
        (void)send_status(context->client_fd, STATUS_CONTENT_TOO_LARGE);
    } else if (parse_result != PROTOCOL_OK) {
        (void)send_status(context->client_fd, STATUS_BAD_REQUEST);
    } else if (request.method == METHOD_GET ||
               request.method == METHOD_HEAD) {
        (void)handle_get_or_head(context, &request);
    } else if (request.method == METHOD_PUT) {
        (void)handle_put(context, &request);
    } else {
        (void)send_status(
            context->client_fd,
            STATUS_METHOD_NOT_ALLOWED
        );
    }

    /* Uma operação por conexão: fecha o socket e descarta o estado da thread */
    close(context->client_fd);
    free(context);
    return NULL;
}

/* Configura a CLI e a raiz; aceita conexões e cria os atendimentos concorrentes */
int main(int argc, char **argv)
{
    const char *host = PROTOCOL_DEFAULT_HOST;
    const char *root = PROTOCOL_DEFAULT_ROOT;
    uint16_t port = PROTOCOL_DEFAULT_PORT;
    uint64_t max_file_size = PROTOCOL_DEFAULT_MAX_FILE_SIZE;
    protocol_limits_t limits;
    int listener_fd;
    int option_index = 0;
    int option;
    struct stat root_stat;

    /* Nomes e argumentos das opções devem permanecer compatíveis com os scripts */
    static const struct option long_options[] = {
        {"host", required_argument, NULL, 'h'},
        {"port", required_argument, NULL, 'p'},
        {"root", required_argument, NULL, 'r'},
        {"max-file-size", required_argument, NULL, 'm'},
        {"help", no_argument, NULL, '?'},
        {NULL, 0, NULL, 0}
    };

    /* Aplica as opções sobre os padrões compartilhados com o protocolo */
    while ((option = getopt_long(
                argc,
                argv,
                "h:p:r:m:?",
                long_options,
                &option_index
            )) != -1) {
        switch (option) {
        case 'h':
            host = optarg;
            break;

        case 'p':
            if (!parse_port(optarg, &port)) {
                fprintf(stderr, "Porta invalida: %s\n", optarg);
                return EXIT_FAILURE;
            }
            break;

        case 'r':
            root = optarg;
            break;

        case 'm':
            if (!parse_u64(optarg, &max_file_size) ||
                max_file_size == 0) {
                fprintf(
                    stderr,
                    "Tamanho maximo invalido: %s\n",
                    optarg
                );
                return EXIT_FAILURE;
            }
            break;

        case '?':
            print_usage(argv[0]);
            return EXIT_SUCCESS;

        default:
            print_usage(argv[0]);
            return EXIT_FAILURE;
        }
    }

    /* Rejeita argumentos extras e valida a raiz antes de abrir a porta */
    if (optind != argc) {
        fprintf(stderr, "Argumento inesperado: %s\n", argv[optind]);
        return EXIT_FAILURE;
    }

    if (root == NULL || strlen(root) == 0 || strlen(root) >= PATH_MAX) {
        fprintf(stderr, "Diretorio raiz invalido ou muito longo\n");
        return EXIT_FAILURE;
    }

    /* Usa o diretório existente ou cria a raiz quando ela ainda não existe */
    if (stat(root, &root_stat) == 0) {
        if (!S_ISDIR(root_stat.st_mode)) {
            fprintf(stderr, "A raiz nao e um diretorio: %s\n", root);
            return EXIT_FAILURE;
        }
    } else if (errno == ENOENT) {
        if (mkdir(root, 0755) < 0) {
            perror("mkdir root");
            return EXIT_FAILURE;
        }
    } else {
        perror("stat root");
        return EXIT_FAILURE;
    }

    /* Cada conexão recebe uma cópia destes limites de validação */
    limits = protocol_default_limits();
    limits.max_file_size = max_file_size;

    /* Queda do cliente não encerra o processo; INT/TERM solicitam parada */
    signal(SIGPIPE, SIG_IGN);
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    /* Inicia a escuta e escreve o diagnóstico de inicialização em stderr */
    listener_fd = create_listener(host, port);

    if (listener_fd < 0) {
        return EXIT_FAILURE;
    }

    fprintf(
        stderr,
        "server: ouvindo em %s:%u, raiz=%s, max-file-size=%" PRIu64 "\n",
        host,
        (unsigned)port,
        root,
        max_file_size
    );

    /* O laço principal aceita conexões sem executar suas transferencias */
    while (server_running) {
        client_context_t *context;
        pthread_t thread;
        int client_fd;
        int thread_result;

        client_fd = accept(listener_fd, NULL, NULL);

        if (client_fd < 0) {
            if (errno == EINTR) {
                continue;
            }

            perror("accept");
            break;
        }

        /* Aloca estado próprio; falhas antes da thread liberam socket e memória */
        context = calloc(1, sizeof(*context));

        if (context == NULL) {
            perror("calloc");
            close(client_fd);
            continue;
        }

        context->client_fd = client_fd;
        context->limits = limits;

        if (snprintf(
                context->root,
                sizeof(context->root),
                "%s",
                root
            ) < 0 || strlen(root) >= sizeof(context->root)) {
            fprintf(stderr, "Diretorio raiz muito longo\n");
            close(client_fd);
            free(context);
            continue;
        }

        /* A thread passa a cuidar da conexão e da liberação do contexto */
        thread_result = pthread_create(
            &thread,
            NULL,
            client_thread,
            context
        );

        if (thread_result != 0) {
            fprintf(
                stderr,
                "pthread_create: %s\n",
                strerror(thread_result)
            );
            close(client_fd);
            free(context);
            continue;
        }

        /* Libera recursos da thread ao terminar, sem exigir join no laço principal */
        thread_result = pthread_detach(thread);

        if (thread_result != 0) {
            fprintf(
                stderr,
                "pthread_detach: %s\n",
                strerror(thread_result)
            );
        }
    }

    /* Fecha a escuta ao sair do laço principal */
    close(listener_fd);
    return EXIT_SUCCESS;
}
