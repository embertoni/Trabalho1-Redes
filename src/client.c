#define _POSIX_C_SOURCE 200809L

#include "protocol.h"

#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <inttypes.h>
#include <netdb.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <limits.h>

#define CLIENT_HEADER_BUFFER (PROTOCOL_MAX_HEADER_LEN + 1)
#define CLIENT_TRANSFER_BUFFER (64U * 1024U)
#define CLIENT_DEFAULT_TIMEOUT_SECONDS 30
#define CLIENT_JSON_STRING_BUFFER 1024

#if defined(O_NOFOLLOW)
#define CLIENT_OPEN_FLAGS O_RDONLY | O_NOFOLLOW
#else
#define CLIENT_OPEN_FLAGS O_RDONLY
#endif

typedef struct {
    const char *host;
    uint16_t port;
    protocol_method_t method;
    const char *remote_path;
    const char *input_path;
    const char *output_path;
    unsigned connect_timeout;
    unsigned io_timeout;
    const char *request_id;
} client_options_t;

typedef struct {
    const char *status;
    protocol_method_t method;
    const char *remote;
    int status_code;
    uint64_t bytes;
    double elapsed_ms;
    int throughput_valid;
    double throughput_mbps;
    const char *error;
} result_data_t;

static void print_usage(const char *program)
{
    fprintf(
        stderr,
        "Uso: %s --host ENDERECO --port PORTA --method METODO "
        "--remote CAMINHO [opcoes]\n\n"
        "Opcoes:\n"
        "  --host ENDERECO          endereco do servidor\n"
        "  --port PORTA             porta TCP\n"
        "  --method METODO         GET, PUT ou HEAD\n"
        "  --remote CAMINHO        caminho remoto\n"
        "  --input ARQUIVO         arquivo local para PUT\n"
        "  --output ARQUIVO        arquivo local para GET\n"
        "  --connect-timeout SEG   timeout de conexao\n"
        "  --io-timeout SEG        timeout de leitura/escrita\n"
        "  --request-id ID          identificador opcional\n"
        "  --help                   mostra esta ajuda\n",
        program
    );
}

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

static int parse_positive_seconds(const char *text, unsigned *value)
{
    char *end = NULL;
    unsigned long parsed;

    if (text == NULL || text[0] == '\0') {
        return 0;
    }

    errno = 0;
    parsed = strtoul(text, &end, 10);

    if (errno != 0 || end == text || *end != '\0' ||
        parsed == 0 || parsed > 86400UL) {
        return 0;
    }

    *value = (unsigned)parsed;
    return 1;
}

static int connect_to_server(
    const client_options_t *options
)
{
    struct addrinfo hints;
    struct addrinfo *results = NULL;
    struct addrinfo *current;
    char port_text[16];
    int socket_fd = -1;
    int result;
    struct timeval timeout;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    snprintf(port_text, sizeof(port_text), "%u", (unsigned)options->port);

    result = getaddrinfo(
        options->host,
        port_text,
        &hints,
        &results
    );

    if (result != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(result));
        return -1;
    }

    timeout.tv_sec = (time_t)options->io_timeout;
    timeout.tv_usec = 0;

    for (current = results; current != NULL; current = current->ai_next) {
        socket_fd = socket(
            current->ai_family,
            current->ai_socktype,
            current->ai_protocol
        );

        if (socket_fd < 0) {
            continue;
        }

        if (setsockopt(
                socket_fd,
                SOL_SOCKET,
                SO_RCVTIMEO,
                &timeout,
                sizeof(timeout)
            ) < 0 ||
            setsockopt(
                socket_fd,
                SOL_SOCKET,
                SO_SNDTIMEO,
                &timeout,
                sizeof(timeout)
            ) < 0) {
            close(socket_fd);
            socket_fd = -1;
            continue;
        }

        if (connect(
                socket_fd,
                current->ai_addr,
                current->ai_addrlen
            ) == 0) {
            break;
        }

        close(socket_fd);
        socket_fd = -1;
    }

    freeaddrinfo(results);
    return socket_fd;
}

static double monotonic_ms(void)
{
    struct timespec now;

    if (clock_gettime(CLOCK_MONOTONIC, &now) < 0) {
        return 0.0;
    }

    return (double)now.tv_sec * 1000.0 +
           (double)now.tv_nsec / 1000000.0;
}

static int write_all_fd(int fd, const void *buffer, size_t length)
{
    const unsigned char *current = buffer;
    size_t written = 0;

    while (written < length) {
        ssize_t result;

        do {
            result = write(fd, current + written, length - written);
        } while (result < 0 && errno == EINTR);

        if (result <= 0) {
            return -1;
        }

        written += (size_t)result;
    }

    return 0;
}

static int send_file(
    int socket_fd,
    int file_fd,
    uint64_t length
)
{
    unsigned char buffer[CLIENT_TRANSFER_BUFFER];
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

        if (protocol_send_all(
                socket_fd,
                buffer,
                (size_t)bytes_read
            ) != bytes_read) {
            return -1;
        }

        remaining -= (uint64_t)bytes_read;
    }

    return 0;
}

static int receive_file(
    int socket_fd,
    int file_fd,
    uint64_t length
)
{
    unsigned char buffer[CLIENT_TRANSFER_BUFFER];
    uint64_t remaining = length;

    while (remaining > 0) {
        size_t requested = sizeof(buffer);
        ssize_t bytes_received;

        if (remaining < (uint64_t)requested) {
            requested = (size_t)remaining;
        }

        do {
            bytes_received = recv(
                socket_fd,
                buffer,
                requested,
                0
            );
        } while (bytes_received < 0 && errno == EINTR);

        if (bytes_received <= 0) {
            return -1;
        }

        if (write_all_fd(
                file_fd,
                buffer,
                (size_t)bytes_received
            ) < 0) {
            return -1;
        }

        remaining -= (uint64_t)bytes_received;
    }

    return 0;
}

static int make_output_temp(
    const char *output_path,
    char *temporary_path,
    size_t temporary_capacity
)
{
    int written;

    written = snprintf(
        temporary_path,
        temporary_capacity,
        "%s.tmp-XXXXXX",
        output_path
    );

    if (written < 0 || (size_t)written >= temporary_capacity) {
        return -1;
    }

    return mkstemp(temporary_path);
}

static void json_print_string(const char *text)
{
    const unsigned char *current = (const unsigned char *)text;

    putchar('"');

    if (text != NULL) {
        while (*current != '\0') {
            switch (*current) {
            case '"':
                fputs("\\\"", stdout);
                break;
            case '\\':
                fputs("\\\\", stdout);
                break;
            case '\n':
                fputs("\\n", stdout);
                break;
            case '\r':
                fputs("\\r", stdout);
                break;
            case '\t':
                fputs("\\t", stdout);
                break;
            default:
                if (*current < 0x20U) {
                    printf("\\u%04x", (unsigned)*current);
                } else {
                    putchar((int)*current);
                }
                break;
            }
            ++current;
        }
    }

    putchar('"');
}

static void print_result(const result_data_t *result)
{
    printf(
        "{\"status\":"
    );
    json_print_string(result->status);
    printf(",\"method\":");
    json_print_string(protocol_method_to_string(result->method));
    printf(",\"remote\":");
    json_print_string(result->remote);
    printf(",\"status_code\":%d,\"bytes\":%" PRIu64
           ",\"elapsed_ms\":%.3f,\"throughput_mbps\":",
           result->status_code,
           result->bytes,
           result->elapsed_ms);

    if (result->throughput_valid) {
        printf("%.3f", result->throughput_mbps);
    } else {
        printf("null");
    }

    printf(",\"error\":");
    if (result->error != NULL) {
        json_print_string(result->error);
    } else {
        printf("null");
    }
    puts("}");
}

static void set_error(
    result_data_t *result,
    const char *error
)
{
    result->status = "error";
    result->error = error;
    result->throughput_valid = 0;
}

static const char *error_for_status(int status_code)
{
    switch (status_code) {
    case STATUS_BAD_REQUEST:
        return "bad_request";
    case STATUS_NOT_FOUND:
        return "remote_file_not_found";
    case STATUS_METHOD_NOT_ALLOWED:
        return "method_not_allowed";
    case STATUS_CONTENT_TOO_LARGE:
        return "content_too_large";
    case STATUS_INTERNAL_SERVER_ERROR:
        return "remote_internal_error";
    case STATUS_NOT_IMPLEMENTED:
        return "not_implemented";
    case STATUS_INSUFFICIENT_STORAGE:
        return "remote_storage_error";
    default:
        return "remote_error";
    }
}

static int run_request(
    const client_options_t *options,
    result_data_t *result
)
{
    char request[PROTOCOL_MAX_HEADER_LEN];
    char response_header[CLIENT_HEADER_BUFFER];
    char temporary_path[PATH_MAX];
    struct stat input_stat;
    protocol_response_t response;
    int request_length;
    int socket_fd = -1;
    int input_fd = -1;
    int output_fd = -1;
    int temporary_created = 0;
    int rc = -1;
    double started_ms;
    double ended_ms;

    started_ms = monotonic_ms();

    if (options->method == METHOD_PUT) {
        input_fd = open(options->input_path, CLIENT_OPEN_FLAGS);
        if (input_fd < 0) {
            set_error(result, "input_open_failed");
            goto finish;
        }

        if (fstat(input_fd, &input_stat) < 0 ||
            !S_ISREG(input_stat.st_mode) ||
            input_stat.st_size < 0) {
            set_error(result, "input_not_regular_file");
            goto finish;
        }
    }

    request_length = protocol_build_request(
        request,
        sizeof(request),
        options->method,
        options->remote_path,
        options->method == METHOD_PUT
            ? (uint64_t)input_stat.st_size
            : 0
    );

    if (request_length < 0) {
        set_error(result, "request_build_failed");
        goto finish;
    }

    socket_fd = connect_to_server(options);

    if (socket_fd < 0) {
        set_error(result, "connection_failed");
        goto finish;
    }

    if (protocol_send_all(
            socket_fd,
            request,
            (size_t)request_length
        ) != (ssize_t)request_length) {
        set_error(result, "request_send_failed");
        goto finish;
    }

    if (options->method == METHOD_PUT) {
        if (send_file(
                socket_fd,
                input_fd,
                (uint64_t)input_stat.st_size
            ) < 0) {
            set_error(result, "input_send_failed");
            goto finish;
        }
    }

    {
        ssize_t response_length = protocol_recv_header(
            socket_fd,
            response_header,
            sizeof(response_header)
        );

        if (response_length <= 0 ||
            protocol_parse_response(
                response_header,
                (size_t)response_length,
                &response
            ) != PROTOCOL_OK) {
            set_error(result, "invalid_response");
            goto finish;
        }
    }

    result->status_code = response.status_code;

    if (response.status_code < 200 || response.status_code >= 300) {
        set_error(result, error_for_status(response.status_code));
        goto finish;
    }

    if (options->method == METHOD_GET) {
        output_fd = make_output_temp(
            options->output_path,
            temporary_path,
            sizeof(temporary_path)
        );

        if (output_fd < 0) {
            set_error(result, "output_open_failed");
            goto finish;
        }

        temporary_created = 1;

        if (receive_file(
                socket_fd,
                output_fd,
                response.content_length
            ) < 0) {
            set_error(result, "response_body_incomplete");
            goto finish;
        }

        if (fsync(output_fd) < 0 || close(output_fd) < 0) {
            output_fd = -1;
            set_error(result, "output_close_failed");
            goto finish;
        }

        output_fd = -1;

        if (rename(temporary_path, options->output_path) < 0) {
            set_error(result, "output_publish_failed");
            goto finish;
        }

        temporary_created = 0;
        result->bytes = response.content_length;
    } else if (options->method == METHOD_PUT) {
        result->bytes = (uint64_t)input_stat.st_size;

        if (response.content_length != 0) {
            set_error(result, "unexpected_response_body");
            goto finish;
        }
    } else {
        if (response.content_length != 0) {
            set_error(result, "unexpected_head_body_length");
            goto finish;
        }
    }

    result->status = "ok";
    result->error = NULL;
    rc = 0;

finish:
    ended_ms = monotonic_ms();
    result->elapsed_ms = ended_ms - started_ms;

    if (result->elapsed_ms > 0.0 &&
        result->bytes > 0 &&
        result->status != NULL &&
        strcmp(result->status, "ok") == 0) {
        result->throughput_valid = 1;
        result->throughput_mbps =
            ((double)result->bytes * 8.0) /
            (result->elapsed_ms / 1000.0) /
            1000000.0;
    }

    if (output_fd >= 0) {
        close(output_fd);
    }

    if (temporary_created) {
        unlink(temporary_path);
    }

    if (input_fd >= 0) {
        close(input_fd);
    }

    if (socket_fd >= 0) {
        close(socket_fd);
    }

    return rc;
}

int main(int argc, char **argv)
{
    client_options_t options;
    result_data_t result;
    int option;
    int option_index = 0;
    int request_result;

    static const struct option long_options[] = {
        {"host", required_argument, NULL, 'h'},
        {"port", required_argument, NULL, 'p'},
        {"method", required_argument, NULL, 'm'},
        {"remote", required_argument, NULL, 'r'},
        {"input", required_argument, NULL, 'i'},
        {"output", required_argument, NULL, 'o'},
        {"connect-timeout", required_argument, NULL, 'c'},
        {"io-timeout", required_argument, NULL, 't'},
        {"request-id", required_argument, NULL, 'd'},
        {"help", no_argument, NULL, '?'},
        {NULL, 0, NULL, 0}
    };

    memset(&options, 0, sizeof(options));
    options.port = PROTOCOL_DEFAULT_PORT;
    options.connect_timeout = CLIENT_DEFAULT_TIMEOUT_SECONDS;
    options.io_timeout = CLIENT_DEFAULT_TIMEOUT_SECONDS;

    while ((option = getopt_long(
                argc,
                argv,
                "h:p:m:r:i:o:c:t:d:?",
                long_options,
                &option_index
            )) != -1) {
        switch (option) {
        case 'h':
            options.host = optarg;
            break;
        case 'p':
            if (!parse_port(optarg, &options.port)) {
                fprintf(stderr, "Porta invalida: %s\n", optarg);
                return EXIT_FAILURE;
            }
            break;
        case 'm':
            options.method = protocol_method_from_string(optarg);
            if (options.method == METHOD_INVALID) {
                fprintf(stderr, "Metodo invalido: %s\n", optarg);
                return EXIT_FAILURE;
            }
            break;
        case 'r':
            options.remote_path = optarg;
            break;
        case 'i':
            options.input_path = optarg;
            break;
        case 'o':
            options.output_path = optarg;
            break;
        case 'c':
            if (!parse_positive_seconds(optarg, &options.connect_timeout)) {
                fprintf(stderr, "Timeout de conexao invalido: %s\n", optarg);
                return EXIT_FAILURE;
            }
            break;
        case 't':
            if (!parse_positive_seconds(optarg, &options.io_timeout)) {
                fprintf(stderr, "Timeout de I/O invalido: %s\n", optarg);
                return EXIT_FAILURE;
            }
            break;
        case 'd':
            options.request_id = optarg;
            break;
        case '?':
            print_usage(argv[0]);
            return EXIT_SUCCESS;
        default:
            print_usage(argv[0]);
            return EXIT_FAILURE;
        }
    }

    (void)options.connect_timeout;
    (void)options.request_id;

    if (optind != argc || options.host == NULL ||
        options.remote_path == NULL || options.method == METHOD_INVALID) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    if (!protocol_validate_path(
            options.remote_path,
            PROTOCOL_MAX_PATH_LEN
        )) {
        fprintf(stderr, "Caminho remoto invalido\n");
        return EXIT_FAILURE;
    }

    if (options.method == METHOD_GET && options.output_path == NULL) {
        fprintf(stderr, "GET exige --output\n");
        return EXIT_FAILURE;
    }

    if (options.method == METHOD_PUT && options.input_path == NULL) {
        fprintf(stderr, "PUT exige --input\n");
        return EXIT_FAILURE;
    }

    if (options.method != METHOD_GET && options.output_path != NULL) {
        fprintf(stderr, "--output somente pode ser usado com GET\n");
        return EXIT_FAILURE;
    }

    if (options.method != METHOD_PUT && options.input_path != NULL) {
        fprintf(stderr, "--input somente pode ser usado com PUT\n");
        return EXIT_FAILURE;
    }

    memset(&result, 0, sizeof(result));
    result.status = "error";
    result.method = options.method;
    result.remote = options.remote_path;
    result.status_code = 0;
    result.error = "unknown_error";

    request_result = run_request(&options, &result);
    print_result(&result);

    return request_result == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
