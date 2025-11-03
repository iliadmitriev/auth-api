# Auth API

A modern Python web authentication API using aiohttp, SQLAlchemy 2.0, Pydantic, and Redis.

## Setup with uv (recommended)

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

### Prerequisites
- Python 3.9+
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