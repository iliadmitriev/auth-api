# auth-api

New realization of https://github.com/iliadmitriev/auth
started from a scratch

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
POSTGRES_HOST=192.168.10.1
POSTGRES_PORT=5432
POSTGRES_DB=auth
POSTGRES_USER=auth
POSTGRES_PASSWORD=authsecret
REDIS_LOCATION=redis://192.168.10.1:6379/0
_EOF_

export $(cat .env | xargs)

```
secret key should be a random string which is keeped in secret
4. create db instances (postgres, redis)
```shell
docker run -d --name auth-redis --hostname auth-redis \
    -p 6379:6379 redis:6.2.1-alpine3.13

docker run -d --name auth-postgres --hostname auth-postgres \
    -p 5432:5432 --env-file .env postgres:13-alpine
```
5. install pip modules from project requirements
```shell
pip install -r requirements.txt
```
6. migrate alembic revisions
```shell
alembic upgrade head
```


# How to use

Read api documentation http://localhost:8080/auth/v1/docs
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