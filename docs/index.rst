auth-api
========

|CI unittests| |codecov| |CodeFactor| |Known Vulnerabilities|

New realization of https://github.com/iliadmitriev/auth started from a
scratch

installation
============

1. checkout repository
2. create and activate virtual environment

.. code:: shell

   python3 -m venv venv
   source venv/bin/activate

3. create ``.env`` file with environment variables and export them to
   shell

.. code:: shell

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

secret key should be a random string which is kept in secret 4. create
db instances (postgres, redis)

.. code:: shell

   docker run -d --name auth-redis --hostname auth-redis \
       -p 6379:6379 redis:6.2.5-alpine3.14

   docker run -d --name auth-postgres --hostname auth-postgres \
       -p 5432:5432 --env-file .env postgres:13.4-alpine3.14

5. install pip modules from project requirements

.. code:: shell

   pip install -r requirements.txt

6. migrate alembic revisions

.. code:: shell

   alembic upgrade head

7. run

.. code:: shell

   python3 main.py

How to use
==========

Read api documentation http://localhost:8080/auth/v1/docs

With curl
---------

1. Register user

.. code:: shell

   curl -v -F password=321123 -F password2=321123 -F email=user@example.com \
     --url http://localhost:8080/auth/v1/register

2. Get a token pair (access and refresh)

.. code:: shell

   curl -v -F password=321123 -F email=user@example.com \
     --url http://localhost:8080/auth/v1/login

access_token - is needed to authenticate your queries (it expires in 5
minutes)

refresh_token - is needed to refresh access token (it expires in 24
hours)

3. Refresh access token

.. code:: shell

   curl -v --url http://localhost:8080/auth/v1/refresh \
    -F refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo3LCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJqdGkiOiIwMWVjNjRhOWZlZjc0ZWIwOWViMGI1YmY1NGViOWVjMSIsInRva2VuX3R5cGUiOiJyZWZyZXNoX3Rva2VuIiwiZXhwIjoxNjE1MzA0MDQ2fQ.QyRVKKkxRNcql84ri6HPcL78D348LOPKH_BmKGUdpFo

With HTTPie
-----------

install `HTTPie <https://github.com/httpie/httpie>`__,
`httpie-jwt-auth <https://github.com/teracyhq/httpie-jwt-auth>`__,
`jq <https://github.com/stedolan/jq>`__

1. set login and password to environment variables

.. code:: shell

   AUTH_EMAIL=admin@example.com
   AUTH_PASS=321123

2. Login and get refresh token (expires in 24h)

.. code:: shell

   REFRESH_TOKEN=$(http :8080/auth/v1/login email=$AUTH_EMAIL password=$AUTH_PASS | jq --raw-output '.refresh_token')

3. Using refresh token, get an access token(expires in 5 min, repeat
   step 3 in 5 min)

.. code:: shell

   ACCESS_TOKEN=$(http :8080/auth/v1/refresh refresh_token=$REFRESH_TOKEN | jq --raw-output '.access_token') 

4. Make request to users api with access token

.. code:: shell

   http -v -A jwt -a $ACCESS_TOKEN :8080/auth/v1/users

Testing
=======

Run tests
~~~~~~~~~

.. code:: shell

   pytest -v --cov=.

Run tests with coverage
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   pytest -v --cov=. --cov-report=term-missing --cov-fail-under=100

Run tests with html report
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   # run tests and generate report
   pytest -v --cov=. --cov-report=term-missing --cov-fail-under=100 --cov-report=html

   # open report
   open htmlcov/index.html 

Docker
======

Build
-----

.. code:: shell

   docker build -t auth_api ./

Run
---

.. code:: shell

   docker run -d -p 8080:8080 --name auth-api \
     --hostname auth-api --env-file .env auth_api

Docker-compose
==============

1. create ``.env`` file with environment variables and export them to
   shell

.. code:: shell

   cat > .env << _EOF_
   SECRET_KEY=testsecretkey
   POSTGRES_HOST=auth-postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=auth
   POSTGRES_USER=auth
   POSTGRES_PASSWORD=authsecret
   REDIS_LOCATION=redis://auth-redis:6379/0
   _EOF_

2. pull, build and run

.. code:: shell

   docker-compose up -d

3. apply migrations

.. code:: shell

   docker-compose exec api alembic upgrade head

full cleanup

.. code:: shell

   docker-compose down --volumes --remove-orphans --rmi all

.. |CI unittests| image:: https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml/badge.svg
   :target: https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml
.. |codecov| image:: https://codecov.io/gh/iliadmitriev/auth-api/branch/master/graph/badge.svg?token=RF1H05TVCH
   :target: https://codecov.io/gh/iliadmitriev/auth-api
.. |CodeFactor| image:: https://www.codefactor.io/repository/github/iliadmitriev/auth-api/badge
   :target: https://www.codefactor.io/repository/github/iliadmitriev/auth-api
.. |Known Vulnerabilities| image:: https://snyk.io/test/github/iliadmitriev/auth-api/badge.svg
   :target: https://snyk.io/test/github/iliadmitriev/auth-api
