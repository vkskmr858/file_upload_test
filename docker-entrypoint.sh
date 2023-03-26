#!/bin/sh

exec gunicorn --bind 0.0.0.0:80 "app:create_app()"

# exec gunicorn --bind 0.0.0.0:80 \
#     --certfile=cert.pem \
#     --keyfile=key.pem \
#     --ssl-version=TLSv1_2 \
#     --ciphers=ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256 \
#      "app:create_app()"
