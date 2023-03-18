FROM python:3.10
RUN apt-get update && \
    apt-get install -y openssl



#RUN openssl req -newkey rsa:2048 -nodes -keyout key.pem -out csr.pem
#RUN openssl x509 -signkey key.pem -in csr.pem -req -days 365 -out cert.pem


WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN openssl genrsa -out private_key.pem 2048
RUN openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem
COPY . .
CMD ["/bin/bash", "docker-entrypoint.sh"]