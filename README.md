# Auth API

[![CI unittests](https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml/badge.svg)](https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml)
[![codecov](https://codecov.io/gh/iliadmitriev/auth-api/branch/master/graph/badge.svg?token=RF1H05TVCH)](https://codecov.io/gh/iliadmitriev/auth-api)
[![CodeFactor](https://www.codefactor.io/repository/github/iliadmitriev/auth-api/badge)](https://www.codefactor.io/repository/github/iliadmitriev/auth-api)
[![Documentation Status](https://readthedocs.org/projects/auth-api/badge/?version=latest)](https://auth-api.readthedocs.io/en/latest/?badge=latest)

JWT auth service for educational purposes. It's build using aiohttp, asyncpg, redis, SQLAlchemy, alembic, pydantic, PyJWT, pytest 

New realization of https://github.com/iliadmitriev/auth
started from a scratch

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Setup with Docker](#setup-with-docker)
  * [PostgreSQL Database](#postgresql-database)
  * [Redis Cache](#redis-cache)
- [Running the Application](#running-the-application)
- [API Usage Examples](#api-usage-examples)
  * [User Registration](#user-registration)
  * [User Login](#user-login)
  * [Token Refresh](#token-refresh)
  * [User Management](#user-management)
- [Development](#development)
  * [Pre-commit Hooks](#pre-commit-hooks)
  * [Testing](#testing)
  * [Code Quality](#code-quality)

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for fast dependency management
- Docker and Docker Compose (for database services)
- PostgreSQL 13+ (when running without Docker)
- Redis 6+ (when running without Docker)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iliadmitriev/auth-api.git
   cd auth-api
   ```

2. Install uv if you haven't already:
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or using pip
   pip install uv
   ```

3. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# Application settings
APP_PORT=8080
APP_HOST=0.0.0.0

# Database settings
POSTGRES_DB=auth
POSTGRES_USER=auth
POSTGRES_PASSWORD=authsecret
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis settings
REDIS_LOCATION=redis://localhost:6379/0

# JWT settings
SECRET_KEY=your-secret-key-here
JWT_EXP_ACCESS_SECONDS=300
JWT_EXP_REFRESH_SECONDS=86400
JWT_ALGORITHM=HS256

# Database engine (use postgresql+asyncpg for asyncpg)
ENGINE=postgresql+asyncpg
```

## Setup with Docker

### PostgreSQL Database

Start PostgreSQL using Docker:

```bash
# Create a docker-compose.yml file for database services
cat > docker-compose.db.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:13.4-alpine3.14
    container_name: auth-postgres
    hostname: auth-postgres
    environment:
      POSTGRES_DB: \${POSTGRES_DB:-auth}
      POSTGRES_USER: \${POSTGRES_USER:-auth}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-authsecret}
    ports:
      - "\${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - auth-network

  redis:
    image: redis:6.2.5-alpine3.14
    container_name: auth-redis
    hostname: auth-redis
    ports:
      - "6379:6379"
    networks:
      - auth-network

volumes:
  postgres_data:

networks:
  auth-network:
    driver: bridge
EOF

# Start the database services
docker-compose -f docker-compose.db.yml up -d
```

Apply database migrations:
```bash
# Run migrations
docker-compose -f docker-compose.db.yml exec postgres alembic upgrade head
```

Stop database services:
```bash
# Stop services
docker-compose -f docker-compose.db.yml down
```

### Full Stack with Application

For development with the full stack:

```bash
# Create a complete docker-compose.yml file
cat > docker-compose.yml << EOF
version: '3.8'

services:
  api:
    build: .
    container_name: auth-api
    hostname: auth-api
    ports:
      - "\${APP_PORT:-8080}:\${APP_PORT:-8080}"
    environment:
      - APP_PORT=\${APP_PORT:-8080}
      - APP_HOST=0.0.0.0
      - POSTGRES_DB=\${POSTGRES_DB:-auth}
      - POSTGRES_USER=\${POSTGRES_USER:-auth}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD:-authsecret}
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - REDIS_LOCATION=redis://redis:6379/0
      - SECRET_KEY=\${SECRET_KEY:-your-secret-key-here}
      - JWT_EXP_ACCESS_SECONDS=\${JWT_EXP_ACCESS_SECONDS:-300}
      - JWT_EXP_REFRESH_SECONDS=\${JWT_EXP_REFRESH_SECONDS:-86400}
      - JWT_ALGORITHM=\${JWT_ALGORITHM:-HS256}
      - ENGINE=postgresql+asyncpg
    depends_on:
      - postgres
      - redis
    networks:
      - auth-network

  postgres:
    image: postgres:13.4-alpine3.14
    container_name: auth-postgres
    hostname: auth-postgres
    environment:
      POSTGRES_DB: \${POSTGRES_DB:-auth}
      POSTGRES_USER: \${POSTGRES_USER:-auth}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-authsecret}
    ports:
      - "\${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - auth-network

  redis:
    image: redis:6.2.5-alpine3.14
    container_name: auth-redis
    hostname: auth-redis
    ports:
      - "6379:6379"
    networks:
      - auth-network

volumes:
  postgres_data:

networks:
  auth-network:
    driver: bridge
EOF

# Start the full stack
docker-compose up -d

# Apply migrations
docker-compose exec api alembic upgrade head

# Stop the full stack
docker-compose down
```

## Running the Application

### Local Development

```bash
# Source environment variables
export \$(cat .env | xargs)

# Run the application
uv run python main.py
```

### With Docker

```bash
# Build and run with Docker
docker build -t auth-api .

# Run the container
docker run -d -p 8080:8080 --name auth-api \
  --hostname auth-api --env-file .env auth-api
```

## API Usage Examples

### User Registration

```bash
# Register a new user
curl -v -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret","password2":"secret"}' \
  http://localhost:8080/auth/v1/register

# Response: 200 OK
# {
#   "id": 1,
#   "email": "user@example.com",
#   "is_active": true,
#   "is_superuser": false,
#   "created": "2023-01-01T00:00:00",
#   "last_login": null,
#   "confirmed": false
# }
```

### User Login

```bash
# Login to get JWT tokens
curl -v -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}' \
  http://localhost:8080/auth/v1/login

# Response: 200 OK
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
# }
```

### Token Refresh

```bash
# Refresh access token using refresh token
curl -v -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}' \
  http://localhost:8080/auth/v1/refresh

# Response: 200 OK
# {
#   "access_token": "new_access_token...",
#   "refresh_token": "new_refresh_token..."
# }
```

### User Management (Admin Only)

```bash
# Get list of users (requires admin token)
curl -v -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  http://localhost:8080/auth/v1/users

# Get specific user (requires admin token)
curl -v -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  http://localhost:8080/auth/v1/users/1

# Create new user (requires admin token)
curl -v -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  -d '{"email":"newuser@example.com","password":"secret","is_active":true,"is_superuser":false}' \
  http://localhost:8080/auth/v1/users

# Update user (requires admin token)
curl -v -X PUT -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  -d '{"email":"updated@example.com","is_active":true,"is_superuser":false}' \
  http://localhost:8080/auth/v1/users/1

# Partially update user (requires admin token)
curl -v -X PATCH -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  -d '{"is_active":false}' \
  http://localhost:8080/auth/v1/users/1

# Delete user (requires admin token)
curl -v -X DELETE -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  http://localhost:8080/auth/v1/users/1
```

## Development

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run all pre-commit checks manually
uv run pre-commit run --all-files

# Skip pre-commit hooks (not recommended)
git commit -m "Your message" --no-verify
```

Pre-commit hooks include:
- **Ruff linting**: Code style and error checking
- **Ruff formatting**: Automatic code formatting
- **BasedPyright**: Type checking
- **Pytest**: Unit tests
- **Coverage**: Code coverage check (minimum 60%)

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=.

# Run tests with HTML coverage report
uv run pytest --cov=. --cov-report=html

# Open coverage report
open htmlcov/index.html

# Run specific test file
uv run pytest tests/test_unit.py

# Run tests in verbose mode
uv run pytest -v
```

### Code Quality

```bash
# Run Ruff linting
uv run ruff check .

# Run Ruff formatting
uv run ruff format .

# Run BasedPyright type checking
uv run basedpyright .

# Run all code quality checks
uv run ruff check . && uv run ruff format . && uv run basedpyright .
```

### Continuous Integration

GitHub Actions workflow runs:
- Pre-commit hooks
- Unit tests
- Code coverage check
- Type checking

All checks must pass before merging to master branch.
