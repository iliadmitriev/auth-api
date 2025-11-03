#!/bin/bash
# uv development script for auth-api

echo "Auth API - Development with uv"
echo "==============================="

case "${1:-help}" in
    install)
        echo "Installing dependencies with uv..."
        uv sync
        ;;
    run)
        echo "Running application with uv..."
        uv run python main.py
        ;;
    test)
        echo "Running tests with uv..."
        uv run pytest tests/ -v
        ;;
    test-cov)
        echo "Running tests with coverage..."
        uv run pytest tests/ --cov=. --cov-report=html
        ;;
    shell)
        echo "Activating virtual environment..."
        source .venv/bin/activate
        exec $SHELL
        ;;
    lock)
        echo "Updating lock file..."
        uv lock
        ;;
    sync)
        echo "Syncing dependencies..."
        uv sync
        ;;
    add)
        if [ -z "$2" ]; then
            echo "Usage: $0 add <package>"
            exit 1
        fi
        echo "Adding dependency: $2"
        uv add "$2"
        ;;
    dev)
        if [ -z "$2" ]; then
            echo "Usage: $0 dev <package>"
            exit 1
        fi
        echo "Adding dev dependency: $2"
        uv add --group dev "$2"
        ;;
    help)
        echo "Usage: $0 {install|run|test|test-cov|shell|lock|sync|add PKG|dev PKG|help}"
        echo ""
        echo "  install    Install dependencies"
        echo "  run        Run the application"
        echo "  test       Run tests"
        echo "  test-cov   Run tests with coverage"
        echo "  shell      Activate virtual environment"
        echo "  lock       Update lock file"
        echo "  sync       Sync dependencies"
        echo "  add PKG    Add a dependency"
        echo "  dev PKG    Add a dev dependency"
        echo "  help       Show this help"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac