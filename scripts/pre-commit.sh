#!/bin/bash
# pre-commit.sh - Pre-commit hook script

echo "🔍 Running pre-commit checks..."

# Run Ruff linting
echo "🔧 Running Ruff linting..."
if ! uv run ruff check .; then
    echo "❌ Ruff linting failed"
    exit 1
fi

# Run Ruff formatting
echo "🎨 Running Ruff formatting..."
if ! uv run ruff format .; then
    echo "❌ Ruff formatting failed"
    exit 1
fi

# Run type checking
echo "_typeDefinition Running type checking..."
if ! uv run basedpyright .; then
    echo "❌ Type checking failed"
    exit 1
fi

# Run tests
echo "🧪 Running unit tests..."
if ! uv run pytest tests/ --disable-warnings -q; then
    echo "❌ Unit tests failed"
    exit 1
fi

# Run coverage check
echo "📊 Running coverage check..."
if ! uv run pytest --cov=. --cov-report=term-missing tests/ >/dev/null && ! uv run coverage report --fail-under=60; then
    echo "❌ Coverage check failed"
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0