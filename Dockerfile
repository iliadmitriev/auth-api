FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

ENV USER web-user

RUN addgroup -S $USER && adduser -S $USER -G $USER

WORKDIR $APP_HOME

COPY --chown=$USER requirements.txt $APP_HOME/

RUN apk add --no-cache \
            libpq \
    && apk add --virtual .build-deps \
        build-base python3-dev postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/ \
    && chown -R $USER:$USER $APP_HOME \
    && apk del .build-deps

COPY --chown=$USER . $APP_HOME/

USER $USER

# there shoud be tests

EXPOSE 8080

CMD ["python3","/app/app.py"]