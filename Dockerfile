FROM python:3.8-alpine3.12

RUN addgroup 1000 && adduser -h /home/messages -D -G 1000 messages

WORKDIR /home/messages

COPY requirements.txt /home/messages/

RUN pip3 install --upgrade pip && \
    apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev libffi-dev openssl-dev g++ && \
    apk add --no-cache bash && \
    pip3 install --no-cache-dir -r /home/messages/requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*

COPY wsgi.py        /home/messages/
COPY app            /home/messages/app
# COPY migrations     /home/messages/migrations
COPY tests          /home/messages/tests
COPY entrypoint.sh  /home/messages/
RUN chmod u+x       /home/messages/entrypoint.sh

EXPOSE 80

CMD ["/home/messages/entrypoint.sh"]
