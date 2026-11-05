#define _POSIX_C_SOURCE 200809L

#include "protocol.h"

#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <unistd.h>

static int is_decimal_string(const char *text)
{
    size_t i;

    if (text == NULL || text[0] == '\0') {
        return 0;
    }

    for (i = 0; text[i] != '\0'; ++i) {
        if (!isdigit((unsigned char)text[i])) {
            return 0;
        }
    }

    return 1;
}

static int parse_u64_strict(
    const char *text,
    uint64_t *value
)
{
    char *end = NULL;
    unsigned long long parsed;

    if (!is_decimal_string(text)) {
        return 0;
    }

    errno = 0;
    parsed = strtoull(text, &end, 10);

    if (errno == ERANGE || end == NULL || *end != '\0') {
        return 0;
    }

    *value = (uint64_t)parsed;
    return 1;
}

static int copy_trimmed_token(
    const char *begin,
    const char *end,
    char *output,
    size_t output_capacity
)
{
    size_t length;

    while (begin < end && (*begin == ' ' || *begin == '\t')) {
        ++begin;
    }

    while (end > begin && (end[-1] == ' ' || end[-1] == '\t')) {
        --end;
    }

    length = (size_t)(end - begin);

    if (length + 1 > output_capacity) {
        return 0;
    }

    memcpy(output, begin, length);
    output[length] = '\0';
    return 1;
}

static int header_name_equals(
    const char *begin,
    const char *end,
    const char *expected
)
{
    size_t length = (size_t)(end - begin);
    size_t expected_length = strlen(expected);

    if (length != expected_length) {
        return 0;
    }

    return strncasecmp(begin, expected, expected_length) == 0;
}

static int line_next(
    const char *buffer,
    size_t buffer_length,
    size_t *offset,
    const char **line_begin,
    const char **line_end
)
{
    const char *crlf;

    if (*offset >= buffer_length) {
        return 0;
    }

    crlf = strstr(buffer + *offset, "\r\n");

    if (crlf == NULL || (size_t)(crlf - buffer) >= buffer_length) {
        return 0;
    }

    *line_begin = buffer + *offset;
    *line_end = crlf;
    *offset = (size_t)(crlf - buffer) + 2;

    return 1;
}

protocol_limits_t protocol_default_limits(void)
{
    protocol_limits_t limits;

    limits.max_path_len = PROTOCOL_MAX_PATH_LEN;
    limits.max_header_len = PROTOCOL_MAX_HEADER_LEN;
    limits.max_file_size = PROTOCOL_DEFAULT_MAX_FILE_SIZE;

    return limits;
}

protocol_method_t protocol_method_from_string(const char *text)
{
    if (text == NULL) {
        return METHOD_INVALID;
    }

    if (strcmp(text, "GET") == 0) {
        return METHOD_GET;
    }

    if (strcmp(text, "PUT") == 0) {
        return METHOD_PUT;
    }

    if (strcmp(text, "HEAD") == 0) {
        return METHOD_HEAD;
    }

    return METHOD_INVALID;
}

const char *protocol_method_to_string(protocol_method_t method)
{
    switch (method) {
    case METHOD_GET:
        return "GET";
    case METHOD_PUT:
        return "PUT";
    case METHOD_HEAD:
        return "HEAD";
    default:
        return "INVALID";
    }
}

const char *protocol_reason_phrase(int status_code)
{
    switch (status_code) {
    case STATUS_OK:
        return "OK";
    case STATUS_CREATED:
        return "Created";
    case STATUS_BAD_REQUEST:
        return "Bad Request";
    case STATUS_NOT_FOUND:
        return "Not Found";
    case STATUS_METHOD_NOT_ALLOWED:
        return "Method Not Allowed";
    case STATUS_CONTENT_TOO_LARGE:
        return "Content Too Large";
    case STATUS_INTERNAL_SERVER_ERROR:
        return "Internal Server Error";
    case STATUS_NOT_IMPLEMENTED:
        return "Not Implemented";
    case STATUS_INSUFFICIENT_STORAGE:
        return "Insufficient Storage";
    default:
        return "Unknown";
    }
}

int protocol_validate_path(
    const char *path,
    size_t max_path_len
)
{
    size_t length;
    size_t i;

    if (path == NULL || path[0] != '/') {
        return 0;
    }

    length = strlen(path);

    if (length < 2 || length > max_path_len) {
        return 0;
    }

    if (path[1] == '.' && path[2] == '\0') {
        return 0;
    }

    if (path[1] == '.' && path[2] == '.' && path[3] == '\0') {
        return 0;
    }

    for (i = 1; i < length; ++i) {
        unsigned char current = (unsigned char)path[i];

        if (current == '/' || current == '\0') {
            return 0;
        }

        if (iscntrl(current) || isspace(current)) {
            return 0;
        }
    }

    if (strchr(path, '?') != NULL || strchr(path, '#') != NULL) {
        return 0;
    }

    return 1;
}

ssize_t protocol_find_header_end(
    const char *buffer,
    size_t length,
    size_t max_header_len
)
{
    size_t i;

    if (buffer == NULL) {
        return -1;
    }

    if (length > max_header_len) {
        return -1;
    }

    if (length < 4) {
        return 0;
    }

    for (i = 0; i + 3 < length; ++i) {
        if (buffer[i] == '\r' &&
            buffer[i + 1] == '\n' &&
            buffer[i + 2] == '\r' &&
            buffer[i + 3] == '\n') {
            return (ssize_t)(i + 4);
        }
    }

    return 0;
}

protocol_result_t protocol_parse_request(
    const char *header,
    size_t header_length,
    size_t body_length,
    const protocol_limits_t *limits,
    protocol_request_t *out_request
)
{
    size_t header_end;
    size_t offset = 0;
    const char *line_begin;
    const char *line_end;
    char first_line[1024];
    char method_text[32];
    char path_text[PROTOCOL_MAX_PATH_LEN + 2];
    char version_text[32];
    int consumed = 0;
    int has_content_length = 0;
    uint64_t content_length = 0;
    protocol_method_t method;

    if (header == NULL || limits == NULL || out_request == NULL) {
        return PROTOCOL_INVALID;
    }

    if (header_length == 0 || header_length > limits->max_header_len) {
        return PROTOCOL_TOO_LARGE;
    }

    header_end = (size_t)protocol_find_header_end(
        header,
        header_length,
        limits->max_header_len
    );

    if (header_end == 0 || header_end != header_length) {
        return PROTOCOL_INVALID;
    }

    if (!line_next(
            header,
            header_length,
            &offset,
            &line_begin,
            &line_end)) {
        return PROTOCOL_INVALID;
    }

    if ((size_t)(line_end - line_begin) >= sizeof(first_line)) {
        return PROTOCOL_TOO_LARGE;
    }

    memcpy(first_line, line_begin, (size_t)(line_end - line_begin));
    first_line[line_end - line_begin] = '\0';

    if (sscanf(
            first_line,
            "%31s %256s %31s %n",
            method_text,
            path_text,
            version_text,
            &consumed
        ) != 3) {
        return PROTOCOL_INVALID;
    }

    if ((size_t)consumed != strlen(first_line)) {
        return PROTOCOL_INVALID;
    }

    if (strcmp(version_text, "HTTP/1.1") != 0) {
        return PROTOCOL_INVALID;
    }

    method = protocol_method_from_string(method_text);

    if (method == METHOD_INVALID) {
        return PROTOCOL_UNSUPPORTED;
    }

    if (!protocol_validate_path(path_text, limits->max_path_len)) {
        return PROTOCOL_INVALID;
    }

    while (offset < header_length - 2) {
        const char *colon;
        const char *header_line_end;
        char value[256];

        if (!line_next(
                header,
                header_length - 2,
                &offset,
                &line_begin,
                &header_line_end)) {
            return PROTOCOL_INVALID;
        }

        if (line_begin == header_line_end) {
            return PROTOCOL_INVALID;
        }

        colon = memchr(
            line_begin,
            ':',
            (size_t)(header_line_end - line_begin)
        );

        if (colon == NULL) {
            return PROTOCOL_INVALID;
        }

        if (header_name_equals(line_begin, colon, "Content-Length")) {
            if (has_content_length) {
                return PROTOCOL_INVALID;
            }

            if (!copy_trimmed_token(
                    colon + 1,
                    header_line_end,
                    value,
                    sizeof(value))) {
                return PROTOCOL_INVALID;
            }

            if (!parse_u64_strict(value, &content_length)) {
                return PROTOCOL_INVALID;
            }

            if (content_length > limits->max_file_size) {
                return PROTOCOL_TOO_LARGE;
            }

            has_content_length = 1;
        }
    }

    if (method == METHOD_PUT) {
        if (!has_content_length) {
            return PROTOCOL_INVALID;
        }

        if (body_length > content_length) {
            return PROTOCOL_INVALID;
        }
    } else {
        if (has_content_length || body_length != 0) {
            return PROTOCOL_INVALID;
        }
    }

    memset(out_request, 0, sizeof(*out_request));
    out_request->method = method;
    out_request->content_length = content_length;
    out_request->has_content_length = has_content_length;

    memcpy(out_request->path, path_text, strlen(path_text) + 1);

    return PROTOCOL_OK;
}

protocol_result_t protocol_parse_response(
    const char *header,
    size_t header_length,
    protocol_response_t *out_response
)
{
    size_t offset = 0;
    const char *line_begin;
    const char *line_end;
    char first_line[256];
    char version[32];
    int status_code;
    int consumed = 0;
    int has_content_length = 0;
    uint64_t content_length = 0;

    if (header == NULL || out_response == NULL) {
        return PROTOCOL_INVALID;
    }

    if (header_length == 0 ||
        header_length > PROTOCOL_MAX_HEADER_LEN) {
        return PROTOCOL_INVALID;
    }

    if ((size_t)protocol_find_header_end(
            header,
            header_length,
            PROTOCOL_MAX_HEADER_LEN) != header_length) {
        return PROTOCOL_INVALID;
    }

    if (!line_next(
            header,
            header_length,
            &offset,
            &line_begin,
            &line_end)) {
        return PROTOCOL_INVALID;
    }

    if ((size_t)(line_end - line_begin) >= sizeof(first_line)) {
        return PROTOCOL_INVALID;
    }

    memcpy(first_line, line_begin, (size_t)(line_end - line_begin));
    first_line[line_end - line_begin] = '\0';

    if (sscanf(
            first_line,
            "%31s %d %n",
            version,
            &status_code,
            &consumed
        ) != 2) {
        return PROTOCOL_INVALID;
    }

    if (strcmp(version, "HTTP/1.1") != 0) {
        return PROTOCOL_INVALID;
    }

    if (status_code < 100 || status_code > 599) {
        return PROTOCOL_INVALID;
    }

    while (offset < header_length - 2) {
        const char *colon;
        const char *header_line_end;
        char value[256];

        if (!line_next(
                header,
                header_length - 2,
                &offset,
                &line_begin,
                &header_line_end)) {
            return PROTOCOL_INVALID;
        }

        if (line_begin == header_line_end) {
            return PROTOCOL_INVALID;
        }

        colon = memchr(
            line_begin,
            ':',
            (size_t)(header_line_end - line_begin)
        );

        if (colon == NULL) {
            return PROTOCOL_INVALID;
        }

        if (header_name_equals(line_begin, colon, "Content-Length")) {
            if (has_content_length) {
                return PROTOCOL_INVALID;
            }

            if (!copy_trimmed_token(
                    colon + 1,
                    header_line_end,
                    value,
                    sizeof(value))) {
                return PROTOCOL_INVALID;
            }

            if (!parse_u64_strict(value, &content_length)) {
                return PROTOCOL_INVALID;
            }

            has_content_length = 1;
        }
    }

    if (!has_content_length) {
        return PROTOCOL_INVALID;
    }

    out_response->status_code = status_code;
    out_response->content_length = content_length;

    return PROTOCOL_OK;
}

int protocol_build_request(
    char *buffer,
    size_t capacity,
    protocol_method_t method,
    const char *path,
    uint64_t content_length
)
{
    int written;

    if (buffer == NULL || path == NULL) {
        return -1;
    }

    if (!protocol_validate_path(path, PROTOCOL_MAX_PATH_LEN)) {
        return -1;
    }

    if (method != METHOD_GET &&
        method != METHOD_PUT &&
        method != METHOD_HEAD) {
        return -1;
    }

    if ((method == METHOD_GET || method == METHOD_HEAD) &&
        content_length != 0) {
        return -1;
    }

    if (method == METHOD_PUT) {
        written = snprintf(
            buffer,
            capacity,
            "%s %s HTTP/1.1\r\n"
            "Host: servidor\r\n"
            "Content-Length: %" PRIu64 "\r\n"
            "Connection: close\r\n"
            "\r\n",
            protocol_method_to_string(method),
            path,
            content_length
        );
    } else {
	written = snprintf(
	    buffer,
	    capacity,
	    "%s %s HTTP/1.1\r\n"
	    "Host: servidor\r\n"
	    "Connection: close\r\n"
	    "\r\n",
	    protocol_method_to_string(method),
	    path
	);
    }

    if (written < 0 || (size_t)written >= capacity) {
        return -1;
    }

    return written;
}

int protocol_build_response(
    char *buffer,
    size_t capacity,
    int status_code,
    uint64_t content_length
)
{
    int written;

    if (buffer == NULL || capacity == 0) {
        return -1;
    }

    written = snprintf(
        buffer,
        capacity,
        "HTTP/1.1 %d %s\r\n"
        "Content-Length: %" PRIu64 "\r\n"
        "Connection: close\r\n"
        "\r\n",
        status_code,
        protocol_reason_phrase(status_code),
        content_length
    );

    if (written < 0 || (size_t)written >= capacity) {
        return -1;
    }

    return written;
}

ssize_t protocol_send_all(
    int fd,
    const void *buffer,
    size_t length
)
{
    const unsigned char *current = buffer;
    size_t sent = 0;

    if (buffer == NULL && length != 0) {
        return -1;
    }

    while (sent < length) {
        ssize_t result = send(
            fd,
            current + sent,
            length - sent,
            MSG_NOSIGNAL
        );

        if (result > 0) {
            sent += (size_t)result;
            continue;
        }

        if (result == 0) {
            return 0;
        }

        if (errno == EINTR) {
            continue;
        }

        return -1;
    }

    return (ssize_t)sent;
}

ssize_t protocol_recv_some(
    int fd,
    void *buffer,
    size_t capacity
)
{
    ssize_t result;

    if (buffer == NULL || capacity == 0) {
        return -1;
    }

    do {
        result = recv(fd, buffer, capacity, 0);
    } while (result < 0 && errno == EINTR);

    return result;
}

ssize_t protocol_recv_header(
    int fd,
    char *buffer,
    size_t capacity
)
{
    size_t length = 0;

    if (buffer == NULL || capacity < 5) {
        return -1;
    }

    while (length + 1 < capacity) {
        char byte;
        ssize_t result;

        do {
            result = recv(fd, &byte, 1, 0);
        } while (result < 0 && errno == EINTR);

        if (result == 0) {
            return length == 0 ? 0 : -1;
        }

        if (result < 0) {
            return -1;
        }

        buffer[length++] = byte;

        if (length >= 4 &&
            buffer[length - 4] == '\r' &&
            buffer[length - 3] == '\n' &&
            buffer[length - 2] == '\r' &&
            buffer[length - 1] == '\n') {
            buffer[length] = '\0';
            return (ssize_t)length;
        }
    }

    buffer[capacity - 1] = '\0';
    return -1;
}

int protocol_copy_exact(
    int source_fd,
    int destination_fd,
    uint64_t length
)
{
    unsigned char buffer[64 * 1024];
    uint64_t remaining = length;

    while (remaining > 0) {
        size_t requested = sizeof(buffer);

        if (remaining < requested) {
            requested = (size_t)remaining;
        }

        ssize_t bytes_read;

        do {
            bytes_read = read(source_fd, buffer, requested);
        } while (bytes_read < 0 && errno == EINTR);

        if (bytes_read <= 0) {
            return -1;
        }

        {
            size_t written = 0;

            while (written < (size_t)bytes_read) {
                ssize_t bytes_written;

                do {
                    bytes_written = write(
                        destination_fd,
                        buffer + written,
                        (size_t)bytes_read - written
                    );
                } while (bytes_written < 0 && errno == EINTR);

                if (bytes_written <= 0) {
                    return -1;
                }

                written += (size_t)bytes_written;
            }
        }

        remaining -= (uint64_t)bytes_read;
    }

    return 0;
}
