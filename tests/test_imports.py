"""
Test that the application can be imported and initialized properly.
This ensures that all dependencies work together correctly.
"""

def test_app_import():
    """Test that the app can be imported without errors."""
    from app.auth import init_app
    assert init_app is not None


def test_app_initialization():
    """Test that the app can be initialized without errors."""
    from app.auth import init_app
    app = init_app()
    assert app is not None
    assert hasattr(app, 'router')


def test_settings_import():
    """Test that settings can be imported."""
    from app.settings import SECRET_KEY
    assert SECRET_KEY is not None


def test_dependencies_import():
    """Test that key dependencies can be imported."""
    # Test core dependencies
    import pydantic
    import sqlalchemy

    # Test that versions are reasonable
    assert sqlalchemy.__version__ >= '2.0'
    assert pydantic.__version__ >= '2.0'


if __name__ == "__main__":
    test_app_import()
    test_app_initialization()
    test_settings_import()
    test_dependencies_import()
    print("✅ All import tests passed!")
