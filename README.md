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
3. create `.env` file
```shell
cat > .env << _EOF_
SECRET_KEY=testsecretkey
POSTGRES_HOST=192.168.10.1
POSTGRES_PORT=5432
POSTGRES_DB=auth
POSTGRES_USER=auth
POSTGRES_PASSWORD=authsecret
REDIS_LOCATION=192.168.10.1:6379
```
secret key should be a random string which is keeped in secret
4. create db instances (postgres, redis)
```shell
docker run -d --name auth-redis --hostname auth-redis \
    -p 6379:6379 redis:6.2.1-alpine3.13

docker run -d --name auth-postgres --hostname auth-postgres \
    -p 5432:5432 --env-file .env postgres:13-alpine
```