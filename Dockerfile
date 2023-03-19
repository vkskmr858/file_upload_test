FROM python:3.10
RUN apt-get update && \
    apt-get install -y openssl



#RUN openssl req -newkey rsa:2048 -nodes -keyout key.pem -out csr.pem
#RUN openssl x509 -signkey key.pem -in csr.pem -req -days 365 -out cert.pem


WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN openssl genrsa -out private_key.pem 2048
RUN openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj '/CN=localhost'

RUN openssl dhparam -out dhparam.pem 2048 && \
    openssl ecparam -out ecparam.pem -name prime256v1
    #openssl ciphers -v 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256' > /etc/ssl/ciphers

CMD ["gunicorn", "--bind 0.0.0.0:80","app:create_app()", "--certfile=cert.pem", "--keyfile=key.pem", "--ciphers=ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256", "--dhparam=dhparam.pem"]