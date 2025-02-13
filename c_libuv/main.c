#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <uv.h>

#define PORT 8080

void on_close(uv_handle_t *handle) {
    free(handle);
}

void on_shutdown(uv_shutdown_t *req, int status) {
    if (status) {
        uv_close((uv_handle_t *)req->handle, on_close);
    }
    free(req);
}

void on_write(uv_write_t *req, int status) {
    if (status) {
        fprintf(stderr, "Write failed: %s\n", uv_strerror(status));
    }

    uv_shutdown_t *shutdown_req = (uv_shutdown_t *)malloc(sizeof(uv_shutdown_t));
    if (shutdown_req) {
        uv_shutdown(shutdown_req, (uv_stream_t *)req->handle, on_shutdown);
    }

    free(req);
}

void alloc_buffer(uv_handle_t *handle, size_t suggested_size, uv_buf_t *buf) {
    buf->base = (char *)malloc(suggested_size);
    buf->len = suggested_size;
}

void on_read(uv_stream_t *client, ssize_t nread, const uv_buf_t *buf) {
    if (nread > 0) {
        const char *response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\nConnection: close\r\n\r\nHello, World!";
        uv_buf_t buffer = uv_buf_init((char *)response, strlen(response));

        uv_write_t *req = (uv_write_t *)malloc(sizeof(uv_write_t));
        if (req) {
            uv_write(req, client, &buffer, 1, on_write);
        }
    } else if (nread < 0) {
        uv_close((uv_handle_t *)client, on_close);
    }

    if (buf->base) free(buf->base);
}

void on_new_connection(uv_stream_t *server, int status) {
    if (status < 0) {
        fprintf(stderr, "New connection error: %s\n", uv_strerror(status));
        return;
    }

    uv_tcp_t *client = (uv_tcp_t *)malloc(sizeof(uv_tcp_t));
    if (!client) {
        fprintf(stderr, "Failed to allocate memory for client\n");
        return;
    }

    uv_tcp_init(uv_default_loop(), client);
    if (uv_accept(server, (uv_stream_t *)client) == 0) {
        uv_read_start((uv_stream_t *)client, alloc_buffer, on_read);
    } else {
        uv_close((uv_handle_t *)client, on_close);
    }
}

int main() {
    uv_loop_t *loop = uv_default_loop();
    uv_tcp_t server;

    uv_tcp_init(loop, &server);

    struct sockaddr_in addr;
    uv_ip4_addr("127.0.0.1", PORT, &addr);
    uv_tcp_bind(&server, (const struct sockaddr *)&addr, 0);

    int r = uv_listen((uv_stream_t *)&server, SOMAXCONN, on_new_connection); // Increase backlog
    if (r) {
        fprintf(stderr, "Listen error: %s\n", uv_strerror(r));
        return 1;
    }

    printf("TCP server running on port %d...\n", PORT);
    return uv_run(loop, UV_RUN_DEFAULT);
}