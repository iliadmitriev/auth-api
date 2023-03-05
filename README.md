# auth-api

[![CI unittests](https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml/badge.svg)](https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml)
[![codecov](https://codecov.io/gh/iliadmitriev/auth-api/branch/master/graph/badge.svg?token=RF1H05TVCH)](https://codecov.io/gh/iliadmitriev/auth-api)
[![CodeFactor](https://www.codefactor.io/repository/github/iliadmitriev/auth-api/badge)](https://www.codefactor.io/repository/github/iliadmitriev/auth-api)
[![Documentation Status](https://readthedocs.org/projects/auth-api/badge/?version=latest)](https://auth-api.readthedocs.io/en/latest/?badge=latest)

JWT auth service for educational purposes. It's build using aiohttp, psycopg2, aioredis, SQLAlchemy, alembic, marshmallow, PyJWT, pytest 

New realization of https://github.com/iliadmitriev/auth
started from a scratch

# Contents
- [installation](#installation)
- [How to use](#how-to-use)
  * [With curl](#with-curl)
  * [With HTTPie](#with-httpie)
- [Testing](#testing)
    + [Run tests](#run-tests)
    + [Run tests with coverage](#run-tests-with-coverage)
    + [Run tests with html report](#run-tests-with-html-report)
- [Docker](#docker)
  * [Build](#build)
  * [Run](#run)
- [Docker-compose](#docker-compose)

# installation

1. checkout repository
2. create and activate virtual environment
```shell
python3 -m venv venv
source venv/bin/activate
```
3. create `.env` file with environment variables and export them to shell
```shell
cat > .env << _EOF_
SECRET_KEY=testsecretkey
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=auth
POSTGRES_USER=auth
POSTGRES_PASSWORD=authsecret
REDIS_LOCATION=redis://localhost:6379/0
_EOF_

export $(cat .env | xargs)

```
secret key should be a random string which is kept in secret
4. create db instances (postgres, redis)
```shell
docker run -d --name auth-redis --hostname auth-redis \
    -p 6379:6379 redis:7-alpine

docker run -d --name auth-postgres --hostname auth-postgres \
    -p 5432:5432 --env-file .env postgres:15-alpine
```
5. install pip modules from project requirements
```shell
pip install -r requirements.txt
```
6. migrate alembic revisions
```shell
alembic upgrade head
```
7. run
```shell
python3 main.py
```


# How to use

Read api documentation http://localhost:8080/auth/v1/docs

## With curl
1. Register user 
```shell
curl -v -F password=321123 -F password2=321123 -F email=user@example.com \
  --url http://localhost:8080/auth/v1/register
```
2. Get a token pair (access and refresh)
```shell
curl -v -F password=321123 -F email=user@example.com \
  --url http://localhost:8080/auth/v1/login
```

access_token - is needed to authenticate your queries (it expires in 5 minutes)

refresh_token - is needed to refresh access token (it expires in 24 hours)

3. Refresh access token 
```shell
curl -v --url http://localhost:8080/auth/v1/refresh \
 -F refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo3LCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJqdGkiOiIwMWVjNjRhOWZlZjc0ZWIwOWViMGI1YmY1NGViOWVjMSIsInRva2VuX3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiZXhwIjoxNjE1MzA0MDQ2fQ.QyRVKKkxRNcql84ri6HPcL78D348LOPKH_BmKGUdpFo
 ```

## With HTTPie

install [HTTPie](https://github.com/httpie/httpie), [httpie-jwt-auth](https://github.com/teracyhq/httpie-jwt-auth),
[jq](https://github.com/stedolan/jq)

1. set login and password to environment variables
```shell
AUTH_EMAIL=admin@example.com
AUTH_PASS=321123
```

2. Login and get refresh token (expires in 24h)
```shell
REFRESH_TOKEN=$(http :8080/auth/v1/login email=$AUTH_EMAIL password=$AUTH_PASS | jq --raw-output '.refresh_token')
```

3. Using refresh token, get an access token(expires in 5 min, repeat step 3 in 5 min)
```shell
ACCESS_TOKEN=$(http :8080/auth/v1/refresh refresh_token=$REFRESH_TOKEN | jq --raw-output '.access_token') 
```

4. Make request to users api with access token
```shell
http -v -A jwt -a $ACCESS_TOKEN :8080/auth/v1/users
```

# Testing

### Run tests
```shell
pytest -v --cov=.
```

### Run tests with coverage
```shell
pytest -v --cov=. --cov-report=term-missing --cov-fail-under=100
```

### Run tests with html report
```shell
# run tests and generate report
pytest -v --cov=. --cov-report=term-missing --cov-fail-under=100 --cov-report=html

# open report
open htmlcov/index.html 
```


# Docker

## Build 

```shell
docker build -t auth_api ./
```

## Run 

```shell
docker run -d -p 8080:8080 --name auth-api \
  --hostname auth-api --env-file .env auth_api
```

# Docker-compose

1. create `.env` file with environment variables and export them to shell
```shell
cat > .env << _EOF_
SECRET_KEY=testsecretkey
POSTGRES_HOST=auth-postgres
POSTGRES_PORT=5432
POSTGRES_DB=auth
POSTGRES_USER=auth
POSTGRES_PASSWORD=authsecret
REDIS_LOCATION=redis://auth-redis:6379/0
_EOF_
```

2. pull, build and run
```shell
docker-compose up -d
```

3. apply migrations
```shell
docker-compose exec api alembic upgrade head
```

full cleanup
```shell
docker-compose down --volumes --remove-orphans --rmi all
```
