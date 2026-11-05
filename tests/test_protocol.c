#define _POSIX_C_SOURCE 200809L

#include "protocol.h"

#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static void test_defaults(void)
{
    protocol_limits_t limits = protocol_default_limits();

    assert(limits.max_path_len == PROTOCOL_MAX_PATH_LEN);
    assert(limits.max_header_len == PROTOCOL_MAX_HEADER_LEN);
    assert(limits.max_file_size == PROTOCOL_DEFAULT_MAX_FILE_SIZE);
}

static void test_methods(void)
{
    assert(protocol_method_from_string("GET") == METHOD_GET);
    assert(protocol_method_from_string("PUT") == METHOD_PUT);
    assert(protocol_method_from_string("HEAD") == METHOD_HEAD);
    assert(protocol_method_from_string("POST") == METHOD_INVALID);

    assert(strcmp(protocol_method_to_string(METHOD_GET), "GET") == 0);
    assert(strcmp(protocol_method_to_string(METHOD_PUT), "PUT") == 0);
    assert(strcmp(protocol_method_to_string(METHOD_HEAD), "HEAD") == 0);
}

static void test_status_phrases(void)
{
    assert(strcmp(protocol_reason_phrase(200), "OK") == 0);
    assert(strcmp(protocol_reason_phrase(201), "Created") == 0);
    assert(strcmp(protocol_reason_phrase(400), "Bad Request") == 0);
    assert(strcmp(protocol_reason_phrase(404), "Not Found") == 0);
    assert(strcmp(protocol_reason_phrase(507), "Insufficient Storage") == 0);
    assert(strcmp(protocol_reason_phrase(999), "Unknown") == 0);
}

static void test_paths(void)
{
    assert(protocol_validate_path("/arquivo.bin", 255) == 1);
    assert(protocol_validate_path("/teste.dat", 255) == 1);

    assert(protocol_validate_path("", 255) == 0);
    assert(protocol_validate_path("arquivo.bin", 255) == 0);
    assert(protocol_validate_path("/", 255) == 0);
    assert(protocol_validate_path("/a/b.bin", 255) == 0);
    assert(protocol_validate_path("/../segredo", 255) == 0);
    assert(protocol_validate_path("/./arquivo", 255) == 0);
    assert(protocol_validate_path("/arquivo com espaco", 255) == 0);
    assert(protocol_validate_path("/arquivo?x=1", 255) == 0);
    assert(protocol_validate_path("/arquivo#fragmento", 255) == 0);
    assert(protocol_validate_path("/arquivo", 4) == 0);
}

static void test_header_end(void)
{
    const char *complete =
        "GET /a HTTP/1.1\r\n"
        "Connection: close\r\n"
        "\r\n";

    const char *partial =
        "GET /a HTTP/1.1\r\n"
        "Connection: close\r\n";

    assert(protocol_find_header_end(
               complete,
               strlen(complete),
               PROTOCOL_MAX_HEADER_LEN
           ) == (ssize_t)strlen(complete));

    assert(protocol_find_header_end(
               partial,
               strlen(partial),
               PROTOCOL_MAX_HEADER_LEN
           ) == 0);

    assert(protocol_find_header_end(
               complete,
               strlen(complete),
               4
           ) == -1);
}

static void test_get_request(void)
{
    char buffer[1024];
    protocol_request_t request;
    protocol_limits_t limits = protocol_default_limits();
    int length;

    length = protocol_build_request(
        buffer,
        sizeof(buffer),
        METHOD_GET,
        "/arquivo.bin",
        0
    );

    assert(length > 0);
    assert(strstr(buffer, "GET /arquivo.bin HTTP/1.1\r\n") != NULL);
    assert(strstr(buffer, "Connection: close\r\n") != NULL);

    assert(protocol_parse_request(
               buffer,
               (size_t)length,
               0,
               &limits,
               &request
           ) == PROTOCOL_OK);

    assert(request.method == METHOD_GET);
    assert(strcmp(request.path, "/arquivo.bin") == 0);
    assert(request.has_content_length == 0);
    assert(request.content_length == 0);
}

static void test_head_request(void)
{
    char buffer[1024];
    protocol_request_t request;
    protocol_limits_t limits = protocol_default_limits();
    int length;

    length = protocol_build_request(
        buffer,
        sizeof(buffer),
        METHOD_HEAD,
        "/arquivo.bin",
        0
    );

    assert(length > 0);
    assert(strstr(buffer, "HEAD /arquivo.bin HTTP/1.1\r\n") != NULL);

    assert(protocol_parse_request(
               buffer,
               (size_t)length,
               0,
               &limits,
               &request
           ) == PROTOCOL_OK);

    assert(request.method == METHOD_HEAD);
    assert(strcmp(request.path, "/arquivo.bin") == 0);
}

static void test_put_request(void)
{
    char buffer[1024];
    protocol_request_t request;
    protocol_limits_t limits = protocol_default_limits();
    int length;

    length = protocol_build_request(
        buffer,
        sizeof(buffer),
        METHOD_PUT,
        "/arquivo.bin",
        1234
    );

    assert(length > 0);
    assert(strstr(buffer, "PUT /arquivo.bin HTTP/1.1\r\n") != NULL);
    assert(strstr(buffer, "Content-Length: 1234\r\n") != NULL);

    assert(protocol_parse_request(
               buffer,
               (size_t)length,
               1234,
               &limits,
               &request
           ) == PROTOCOL_OK);

    assert(request.method == METHOD_PUT);
    assert(strcmp(request.path, "/arquivo.bin") == 0);
    assert(request.has_content_length == 1);
    assert(request.content_length == 1234);

    assert(protocol_parse_request(
               buffer,
               (size_t)length,
               12,
               &limits,
               &request
           ) == PROTOCOL_OK);

    assert(protocol_parse_request(
               buffer,
               (size_t)length,
               1235,
               &limits,
               &request
           ) == PROTOCOL_INVALID);
}

static void test_invalid_requests(void)
{
    const char *missing_length =
        "PUT /arquivo.bin HTTP/1.1\r\n"
        "Host: servidor\r\n"
        "Connection: close\r\n"
        "\r\n";

    const char *invalid_path =
        "GET /../segredo HTTP/1.1\r\n"
        "Host: servidor\r\n"
        "Connection: close\r\n"
        "\r\n";

    const char *unsupported_method =
        "POST /arquivo.bin HTTP/1.1\r\n"
        "Host: servidor\r\n"
        "Connection: close\r\n"
        "\r\n";

    protocol_request_t request;
    protocol_limits_t limits = protocol_default_limits();

    assert(protocol_parse_request(
               missing_length,
               strlen(missing_length),
               0,
               &limits,
               &request
           ) == PROTOCOL_INVALID);

    assert(protocol_parse_request(
               invalid_path,
               strlen(invalid_path),
               0,
               &limits,
               &request
           ) == PROTOCOL_INVALID);

    assert(protocol_parse_request(
               unsupported_method,
               strlen(unsupported_method),
               0,
               &limits,
               &request
           ) == PROTOCOL_UNSUPPORTED);
}

static void test_response(void)
{
    char buffer[1024];
    protocol_response_t response;
    int length;

    length = protocol_build_response(
        buffer,
        sizeof(buffer),
        STATUS_OK,
        9876
    );

    assert(length > 0);
    assert(strstr(buffer, "HTTP/1.1 200 OK\r\n") != NULL);
    assert(strstr(buffer, "Content-Length: 9876\r\n") != NULL);

    assert(protocol_parse_response(
               buffer,
               (size_t)length,
               &response
           ) == PROTOCOL_OK);

    assert(response.status_code == STATUS_OK);
    assert(response.content_length == 9876);
}

static void test_socket_helpers(void)
{
    int sockets[2];
    const char message[] =
        "GET /teste.bin HTTP/1.1\r\n"
        "Host: servidor\r\n"
        "Connection: close\r\n"
        "\r\n";
    char received[PROTOCOL_MAX_HEADER_LEN + 1];
    ssize_t received_length;

    assert(socketpair(AF_UNIX, SOCK_STREAM, 0, sockets) == 0);

    assert(protocol_send_all(
               sockets[0],
               message,
               strlen(message)
           ) == (ssize_t)strlen(message));

    received_length = protocol_recv_header(
        sockets[1],
        received,
        sizeof(received)
    );

    assert(received_length == (ssize_t)strlen(message));
    assert(strcmp(received, message) == 0);

    close(sockets[0]);
    close(sockets[1]);
}

static void test_small_buffer(void)
{
    char buffer[8];
    int result;

    result = protocol_build_request(
        buffer,
        sizeof(buffer),
        METHOD_GET,
        "/arquivo.bin",
        0
    );

    assert(result == -1);
}

int main(void)
{
    test_defaults();
    test_methods();
    test_status_phrases();
    test_paths();
    test_header_end();
    test_get_request();
    test_head_request();
    test_put_request();
    test_invalid_requests();
    test_response();
    test_socket_helpers();
    test_small_buffer();

    puts("test_protocol: todos os testes passaram");
    return 0;
}
