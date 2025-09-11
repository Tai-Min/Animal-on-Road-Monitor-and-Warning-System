#include "camera_test.h"
#include <Arduino.h>

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %zu\r\n\r\n";

static esp_err_t jpg_stream_httpd_handler(httpd_req_t *req)
{
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    size_t jpg_buf_len = 0;
    uint8_t *jpg_buf = NULL;
    char part_buf[64];
    bool jpeg_converted = false;

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK)
    {
        Serial.println("Set content type failed");
        return res;
    }

    while (true)
    {
        fb = esp_camera_fb_get();
        if (!fb)
        {
            Serial.println("Camera capture failed");
            goto failure;
        }

        jpeg_converted = frame2jpg(fb, 80, &jpg_buf, &jpg_buf_len);
        if (!jpeg_converted)
        {
            Serial.println("JPEG compression failed");
            goto failure;
        }

        if (res == ESP_OK)
        {
            res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        }

        if (res == ESP_OK)
        {
            int hlen = snprintf(part_buf, sizeof(part_buf), _STREAM_PART, jpg_buf_len);
            if (hlen < 0 || hlen >= sizeof(part_buf))
            {
                Serial.println("Header turncated");
                goto failure;
            }
            else
            {
                res = httpd_resp_send_chunk(req, part_buf, (size_t)hlen);
            }
        }

        if (res == ESP_OK)
        {
            Serial.println("Frame buffer len:");
            Serial.print(fb->len);
            Serial.print(" width: ");
            Serial.print(fb->width);
            Serial.print(" height: ");
            Serial.print(fb->height);
            Serial.print(" bytes per pixel: ");
            Serial.println((fb->width * fb->height) / fb->len);
            httpd_resp_send_chunk(req, (const char *)jpg_buf, jpg_buf_len);
        }
        free(jpg_buf);
        esp_camera_fb_return(fb);

    failure:
        if (jpg_buf)
        {
            free(jpg_buf);
        }

        if (fb)
        {
            esp_camera_fb_return(fb);
        }
    }

    return res;
}

void startTestServer()
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();

    httpd_uri_t stream_uri = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = jpg_stream_httpd_handler,
        .user_ctx = NULL};

    httpd_handle_t stream_httpd = NULL;

    Serial.printf("Starting stream server on port: '%d'\n", config.server_port);
    if (httpd_start(&stream_httpd, &config) == ESP_OK)
    {
        httpd_register_uri_handler(stream_httpd, &stream_uri);
    }
}