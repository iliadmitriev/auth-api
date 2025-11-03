def init_app(argv=None):
    # Import inside function to avoid circular imports
    from app.auth import init_app as _init_app

    return _init_app(argv)
