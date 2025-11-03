# Auth API

[![CI unittests](https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml/badge.svg)](https://github.com/iliadmitriev/auth-api/actions/workflows/ci-unittests.yml)
[![codecov](https://codecov.io/gh/iliadmitriev/auth-api/branch/master/graph/badge.svg?token=RF1H05TVCH)](https://codecov.io/gh/iliadmitriev/auth-api)
[![CodeFactor](https://www.codefactor.io/repository/github/iliadmitriev/auth-api/badge)](https://www.codefactor.io/repository/github/iliadmitriev/auth-api)
[![Documentation Status](https://readthedocs.org/projects/auth-api/badge/?version=latest)](https://auth-api.readthedocs.io/en/latest/?badge=latest)

JWT auth service for educational purposes. Built using aiohttp, SQLAlchemy 2.0, Pydantic, Redis, and modern Python tooling.

## Modern Python Stack

- **Python 3.11+** - Latest Python features and performance improvements
- **aiohttp** - Async HTTP framework
- **SQLAlchemy 2.0** - Modern async ORM
- **Pydantic 2.0** - Data validation and settings management
- **Redis** - Async Redis client
- **Alembic** - Database migrations
- **PyJWT** - JSON Web Token implementation
- **pytest** - Testing framework

## Setup with uv (recommended)

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installed

### Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   # or use uv run to run commands in the environment
   uv run python main.py
   ```

### Running the application

```bash
# Run directly with uv
uv run python main.py

# Or activate the environment first
source .venv/bin/activate
python main.py
```

### Running tests

```bash
uv run pytest
# or with coverage
uv run pytest --cov=.
```

### Development commands

```bash
# Run with uv (recommended)
uv run python main.py

# Install additional dependencies
uv add pytest
uv add black --group dev

# Update lock file after changing pyproject.toml
uv lock

# Sync dependencies after lock file changes
uv sync
```

### Code Quality Tools

This project uses modern Python development tools:

- **Ruff**: Ultra-fast Python linter and formatter
- **BasedPyright**: Type checker with better performance than mypy
- **pytest**: Testing framework

```bash
# Linting with Ruff
uv run ruff check .

# Formatting with Ruff
uv run ruff format .

# Type checking with BasedPyright
uv run basedpyright .

# Run all checks
uv run ruff check . && uv run basedpyright .
```

### Traditional setup (without uv)

If you prefer not to use uv:

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   pip install -e ".[dev]"
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## How to use

Read API documentation at http://localhost:8080/auth/v1/docs

### With curl

1. Register user:
   ```bash
   curl -v -F password=321123 -F password2=321123 -F email=user@example.com \
     --url http://localhost:8080/auth/v1/register
   ```

2. Get a token pair (access and refresh):
   ```bash
   curl -v -F password=321123 -F email=user@example.com \
     --url http://localhost:8080/auth/v1/login
   ```

3. Refresh access token:
   ```bash
   curl -v --url http://localhost:8080/auth/v1/refresh \
    -F refresh_token=YOUR_REFRESH_TOKEN
   ```

### With HTTPie

Install [HTTPie](https://github.com/httpie/httpie), [httpie-jwt-auth](https://github.com/teracyhq/httpie-jwt-auth), [jq](https://github.com/stedolan/jq)

1. Set login and password to environment variables:
   ```bash
   AUTH_EMAIL=admin@example.com
   AUTH_PASS=321123
   ```

2. Login and get refresh token:
   ```bash
   REFRESH_TOKEN=$(http :8080/auth/v1/login email=$AUTH_EMAIL password=$AUTH_PASS | jq --raw-output '.refresh_token')
   ```

3. Using refresh token, get an access token:
   ```bash
   ACCESS_TOKEN=$(http :8080/auth/v1/refresh refresh_token=$REFRESH_TOKEN | jq --raw-output '.access_token') 
   ```

4. Make request to users API with access token:
   ```bash
   http -v -A jwt -a $ACCESS_TOKEN :8080/auth/v1/users
   ```

## Testing

### Run tests
```bash
uv run pytest
```

### Run tests with coverage
```bash
uv run pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```

### Run tests with HTML report
```bash
# Run tests and generate report
uv run pytest --cov=. --cov-report=html

# Open report
open htmlcov/index.html 
```

## Docker

### Build
```bash
docker build -t auth_api ./
```

### Run
```bash
docker run -d -p 8080:8080 --name auth-api \
  --hostname auth-api --env-file .env auth_api
```

## Docker-compose

1. Create `.env` file with environment variables:
   ```bash
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

2. Pull, build and run:
   ```bash
   docker-compose up -d
   ```

3. Apply migrations:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. Full cleanup:
   ```bash
   docker-compose down --volumes --remove-orphans --rmi all
   ```

## Development Workflow

### Code Quality

This project uses modern Python tooling for code quality:

1. **Ruff** for linting and formatting:
   ```bash
   uv run ruff check .          # Check for issues
   uv run ruff format .          # Format code
   ```

2. **BasedPyright** for type checking:
   ```bash
   uv run basedpyright .         # Type check
   ```

3. **pytest** for testing:
   ```bash
   uv run pytest                 # Run tests
   uv run pytest --cov=.         # Run tests with coverage
   ```

### Pre-commit Hooks

Set up pre-commit hooks for automatic code quality checks:
```bash
uv run pre-commit install
```

## Project Structure

```
auth-api/
├── app/                 # Main application package
│   ├── auth.py          # Application initialization
│   ├── middlewares.py   # Custom middlewares
│   └── settings.py      # Application settings
├── backends/            # Database and Redis backends
├── helpers/             # Utility functions and helpers
├── models/              # SQLAlchemy models
├── routes/              # URL routing
├── schemas/             # Pydantic schemas
├── views/               # View classes
├── tests/               # Test suite
├── alembic/             # Database migrations
├── main.py             # Application entry point
└── pyproject.toml      # Project configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.