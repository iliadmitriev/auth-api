import pathlib
from os import environ as env

BASE_PATH = pathlib.Path(__file__).parent.parent

APP_PORT = env.get('APP_PORT', 8080)
APP_HOST = env.get('APP_HOST', '0.0.0.0')

access_log_format = '%r %s %b %t "%a"'

# Provide a default secret key for testing environments
SECRET_KEY = env.get('SECRET_KEY', 'test-secret-key-for-testing')
JWT_EXP_ACCESS_SECONDS = env.get('JWT_EXP_ACCESS_SECONDS', 300)
JWT_EXP_REFRESH_SECONDS = env.get('JWT_EXP_REFRESH_SECONDS', 86400)
JWT_ALGORITHM = env.get('JWT_ALGORITHM', 'HS256')

conf = {
    'engine': env.get('ENGINE', 'postgresql+asyncpg'),  # Use asyncpg engine
    'database': env.get('POSTGRES_DB'),
    'user': env.get('POSTGRES_USER'),
    'password': env.get('POSTGRES_PASSWORD'),
    'host': env.get('POSTGRES_HOST'),
    'port': env.get('POSTGRES_PORT', 5432)
}

dsn = f'{conf["engine"]}://{conf["user"]}:{conf["password"]}'\
        f'@{conf["host"]}:{conf["port"]}/{conf["database"]}'


redis_location = env.get('REDIS_LOCATION')
