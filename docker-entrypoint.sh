#!/bin/sh

exec gunicorn --bind 0.0.0.0:80 "app:create_app()"

# exec gunicorn --bind 0.0.0.0:80 \
#     --certfile=cert.pem \
#     --keyfile=key.pem \
#     --ssl-version=TLSv1_2 \
#     --ciphers=ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA384 \
#      "app:create_app()"
