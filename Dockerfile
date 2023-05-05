FROM python:3.10-alpine

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

ENV USER web-user

RUN addgroup -S -g 1000 $USER && adduser -S -G $USER -u 1000 $USER

WORKDIR $APP_HOME

COPY --chown=$USER requirements.txt $APP_HOME/

RUN apk add --no-cache \
            libpq \
    && apk add --virtual .build-deps \
        build-base python3-dev postgresql-dev \
    && pip install --no-cache-dir --ignore-installed six \
        -r requirements.txt \
    && rm -rf /root/.cache/ \
    && chown -R $USER:$USER $APP_HOME \
    && apk del .build-deps

COPY --chown=$USER:$USER . $APP_HOME/

USER $USER

EXPOSE 8080

CMD ["python3","/app/main.py"]