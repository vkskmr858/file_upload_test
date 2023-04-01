FROM python:3.10
#RUN apt-get update && apt-get install -y libmagic1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .

RUN openssl genrsa -out private_key.pem 2048
RUN openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

CMD ["/bin/bash", "docker-entrypoint.sh"]
