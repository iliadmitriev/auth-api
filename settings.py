import pathlib
from os import environ as env

BASE_PATH = pathlib.Path(__file__).parent

APP_PORT = env.get('APP_PORT', 8080)
APP_HOST = env.get('APP_HOST', '0.0.0.0')

access_log_format = '%r %s %b %t "%a"'

SECRET_KEY = env.get('SECRET_KEY')

conf = {
    'engine': env.get('ENGINE', 'postgresql'),
    'database': env.get('POSTGRES_DB'),
    'user': env.get('POSTGRES_USER'),
    'password': env.get('POSTGRES_PASSWORD'),
    'host': env.get('POSTGRES_HOST'),
    'port': env.get('POSTGRES_PORT', 5432)
}

dsn = f'{conf["engine"]}://{conf["user"]}:{conf["password"]}'\
        f'@{conf["host"]}:{conf["port"]}/{conf["database"]}'

