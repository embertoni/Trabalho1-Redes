#ifndef TRABALHO1_REDES_PROTOCOL_H
#define TRABALHO1_REDES_PROTOCOL_H

/*
 * Contrato compartilhado do protocolo da aplicação.
 *
 * O protocolo implementa um subconjunto controlado de HTTP sobre TCP.
 * A implementação não pretende ser compatível com HTTP completo.
 */

#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Configurações padrão da aplicação. */
#define PROTOCOL_DEFAULT_PORT 9000
#define PROTOCOL_DEFAULT_HOST "0.0.0.0"
#define PROTOCOL_DEFAULT_ROOT "server-data"

/* Limites definidos em docs/CONTRATO_PROTOCOLO.md. */
#define PROTOCOL_MAX_PATH_LEN 255
#define PROTOCOL_MAX_HEADER_LEN 8192
#define PROTOCOL_DEFAULT_MAX_FILE_SIZE (UINT64_C(1073741824))

/* Tamanho máximo razoável para uma linha de cabeçalho. */
#define PROTOCOL_MAX_HEADER_LINE_LEN 4096

/* Resultado genérico das funções do protocolo. */
typedef enum {
    PROTOCOL_OK = 0,
    PROTOCOL_EOF = 1,
    PROTOCOL_INVALID = -1,
    PROTOCOL_IO_ERROR = -2,
    PROTOCOL_TIMEOUT = -3,
    PROTOCOL_TOO_LARGE = -4,
    PROTOCOL_NOT_FOUND = -5,
    PROTOCOL_UNSUPPORTED = -6,
    PROTOCOL_INTERNAL_ERROR = -7
} protocol_result_t;

/* Métodos aceitos pela aplicação. */
typedef enum {
    METHOD_INVALID = 0,
    METHOD_GET,
    METHOD_PUT,
    METHOD_HEAD
} protocol_method_t;

/* Código HTTP retornado pelo servidor. */
typedef enum {
    STATUS_OK = 200,
    STATUS_CREATED = 201,
    STATUS_BAD_REQUEST = 400,
    STATUS_NOT_FOUND = 404,
    STATUS_METHOD_NOT_ALLOWED = 405,
    STATUS_CONTENT_TOO_LARGE = 413,
    STATUS_INTERNAL_SERVER_ERROR = 500,
    STATUS_NOT_IMPLEMENTED = 501,
    STATUS_INSUFFICIENT_STORAGE = 507
} protocol_status_t;

/*
 * Requisição já interpretada.
 *
 * path não inclui a query string. Nesta primeira versão, queries não são
 * aceitas e devem ser rejeitadas pelo parser.
 */
typedef struct {
    protocol_method_t method;
    char path[PROTOCOL_MAX_PATH_LEN + 1];
    uint64_t content_length;
    int has_content_length;
} protocol_request_t;

/*
 * Resposta já interpretada.
 */
typedef struct {
    int status_code;
    uint64_t content_length;
} protocol_response_t;

/*
 * Configurações de limite usadas pelo parser e pelo servidor.
 */
typedef struct {
    size_t max_path_len;
    size_t max_header_len;
    uint64_t max_file_size;
} protocol_limits_t;

/*
 * Retorna os limites padrão do protocolo.
 */
protocol_limits_t protocol_default_limits(void);

/*
 * Converte método textual para enum.
 *
 * Retorna METHOD_INVALID quando o método não é GET, PUT ou HEAD.
 */
protocol_method_t protocol_method_from_string(const char *text);

/*
 * Converte método para texto estático.
 *
 * Nunca retorna NULL para os valores válidos.
 */
const char *protocol_method_to_string(protocol_method_t method);

/*
 * Converte código de status para a frase correspondente.
 *
 * Retorna "Unknown" para códigos não previstos pelo contrato.
 */
const char *protocol_reason_phrase(int status_code);

/*
 * Valida um caminho remoto.
 *
 * O caminho deve ser um nome plano iniciado por '/'.
 * Retorna 1 se válido e 0 se inválido.
 */
int protocol_validate_path(const char *path, size_t max_path_len);

/*
 * Encontra o fim do cabeçalho HTTP no buffer.
 *
 * Retorna:
 * - quantidade de bytes até o final de "\\r\\n\\r\\n", quando encontrado;
 * - 0 quando o cabeçalho ainda está incompleto;
 * - -1 quando o tamanho excede o limite.
 */
ssize_t protocol_find_header_end(
    const char *buffer,
    size_t length,
    size_t max_header_len
);

/*
 * Analisa uma requisição completa, incluindo o cabeçalho.
 *
 * header deve conter pelo menos o terminador "\\r\\n\\r\\n".
 * body_length representa a quantidade de bytes disponíveis depois do cabeçalho.
 *
 * Para GET e HEAD, Content-Length não é permitido nesta versão.
 * Para PUT, Content-Length é obrigatório.
 */
protocol_result_t protocol_parse_request(
    const char *header,
    size_t header_length,
    size_t body_length,
    const protocol_limits_t *limits,
    protocol_request_t *out_request
);

/*
 * Analisa a primeira linha de uma resposta e o Content-Length.
 */
protocol_result_t protocol_parse_response(
    const char *header,
    size_t header_length,
    protocol_response_t *out_response
);

/*
 * Constrói o cabeçalho de uma requisição.
 *
 * Para GET e HEAD, content_length deve ser zero.
 * Para PUT, content_length representa o tamanho do corpo.
 *
 * Retorna:
 * - quantidade de bytes escritos;
 * - -1 em caso de erro ou buffer insuficiente.
 */
int protocol_build_request(
    char *buffer,
    size_t capacity,
    protocol_method_t method,
    const char *path,
    uint64_t content_length
);

/*
 * Constrói o cabeçalho de uma resposta.
 *
 * Retorna:
 * - quantidade de bytes escritos;
 * - -1 em caso de erro ou buffer insuficiente.
 */
int protocol_build_response(
    char *buffer,
    size_t capacity,
    int status_code,
    uint64_t content_length
);

/*
 * Envia exatamente length bytes, tratando send() parcial.
 *
 * Retorna:
 * - length em caso de sucesso;
 * - 0 se a conexão foi encerrada antes do envio;
 * - -1 em caso de erro.
 */
ssize_t protocol_send_all(
    int fd,
    const void *buffer,
    size_t length
);

/*
 * Recebe até capacity bytes, tratando recv() parcial.
 *
 * Esta função é uma operação de uma única chamada recv().
 * O tratamento de mensagens parciais deve ser feito pelo chamador.
 *
 * Retorna:
 * - quantidade recebida;
 * - 0 se a conexão foi encerrada;
 * - -1 em caso de erro.
 */
ssize_t protocol_recv_some(
    int fd,
    void *buffer,
    size_t capacity
);

/*
 * Recebe um cabeçalho até "\\r\\n\\r\\n".
 *
 * Retorna:
 * - tamanho total do cabeçalho recebido;
 * - 0 se a conexão foi encerrada antes do cabeçalho;
 * - -1 em caso de erro ou cabeçalho maior que a capacidade.
 */
ssize_t protocol_recv_header(
    int fd,
    char *buffer,
    size_t capacity
);

/*
 * Copia um arquivo usando I/O binário e exatamente o tamanho informado.
 *
 * source_fd e destination_fd devem estar abertos.
 * Retorna 0 em sucesso e -1 em falha.
 */
int protocol_copy_exact(
    int source_fd,
    int destination_fd,
    uint64_t length
);

#ifdef __cplusplus
}
#endif

#endif /* TRABALHO1_REDES_PROTOCOL_H */
