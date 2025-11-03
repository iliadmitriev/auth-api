
from helpers.errors import (
    PasswordsDontMatch,
    RecordNotFound,
    RefreshTokenNotFound,
    UserIsNotActivated,
)
from helpers.utils import (
    decode_token,
    gen_token_for_user,
    generate_password_hash,
    get_refresh_token,
)
from schemas.users import schemas


class TestUtils:
    """Test utility functions without database dependencies"""

    async def test_generate_password_hash(self):
        password = "test_password"
        hashed = await generate_password_hash(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        # Should be different for different passwords
        hashed2 = await generate_password_hash("different_password")
        assert hashed != hashed2

    async def test_gen_token_for_user(self):
        user_data = {
            'id': 1,
            'email': 'test@example.com',
            'is_active': True,
            'is_superuser': False
        }
        token = await gen_token_for_user(user_data)
        assert 'access_token' in token
        assert 'refresh_token' in token
        assert isinstance(token['access_token'], str)
        assert isinstance(token['refresh_token'], str)

    async def test_decode_token(self):
        user_data = {
            'id': 1,
            'email': 'test@example.com',
            'is_active': True,
            'is_superuser': True
        }
        token_data = await gen_token_for_user(user_data)
        decoded = await decode_token(token_data['access_token'])
        assert decoded['user_id'] == user_data['id']
        assert decoded['email'] == user_data['email']
        assert decoded['scope'] == 'admin'  # Superuser gets admin scope

    async def test_gen_token_for_inactive_user(self):
        user_data = {
            'id': 2,
            'email': 'inactive@example.com',
            'is_active': False,
            'is_superuser': False
        }
        token = await gen_token_for_user(user_data)
        assert 'access_token' in token
        assert 'refresh_token' in token

    async def test_gen_token_for_superuser(self):
        user_data = {
            'id': 3,
            'email': 'admin@example.com',
            'is_active': True,
            'is_superuser': True
        }
        token = await gen_token_for_user(user_data)
        assert 'access_token' in token
        assert 'refresh_token' in token

    async def test_get_refresh_token(self):
        # Create a token payload
        token_payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'jti': 'test-jti'
        }
        refreshed_tokens = await get_refresh_token(token_payload)
        assert 'access_token' in refreshed_tokens
        assert 'refresh_token' in refreshed_tokens
        assert isinstance(refreshed_tokens['access_token'], str)
        assert isinstance(refreshed_tokens['refresh_token'], str)


class TestSchemas:
    """Test Pydantic schemas"""

    def test_registration_schema_valid(self):
        data = {
            'email': 'test@example.com',
            'password': 'secret',
            'password2': 'secret'
        }
        validated = schemas.registration(**data)
        assert validated.email == 'test@example.com'
        assert validated.password == 'secret'
        assert validated.password2 == 'secret'

    def test_registration_schema_password_mismatch(self):
        data = {
            'email': 'test@example.com',
            'password': 'secret',
            'password2': 'different'
        }
        try:
            schemas.registration(**data)
            assert False, "Should have raised validation error"
        except Exception:
            pass  # Expected

    def test_registration_schema_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'password': 'secret',
            'password2': 'secret'
        }
        try:
            schemas.registration(**data)
            assert False, "Should have raised validation error"
        except Exception:
            pass  # Expected

    def test_login_schema_valid(self):
        data = {
            'email': 'test@example.com',
            'password': 'secret'
        }
        validated = schemas.login(**data)
        assert validated.email == 'test@example.com'
        assert validated.password == 'secret'

    def test_login_schema_missing_password(self):
        data = {
            'email': 'test@example.com'
            # Missing password
        }
        try:
            schemas.login(**data)
            assert False, "Should have raised validation error"
        except Exception:
            pass  # Expected

    def test_refresh_token_schema_valid(self):
        data = {
            'refresh_token': 'some_refresh_token'
        }
        validated = schemas.refresh_token(**data)
        assert validated.refresh_token == 'some_refresh_token'

    def test_refresh_token_schema_missing_token(self):
        data = {
            # Missing refresh_token
        }
        try:
            schemas.refresh_token(**data)
            assert False, "Should have raised validation error"
        except Exception:
            pass  # Expected


class TestErrors:
    """Test custom error classes"""

    def test_passwords_dont_match(self):
        error = PasswordsDontMatch("Passwords don't match")
        assert str(error) == "Passwords don't match"
        assert isinstance(error, Exception)

    def test_record_not_found(self):
        error = RecordNotFound("Record not found")
        assert str(error) == "Record not found"
        assert isinstance(error, Exception)

    def test_user_is_not_activated(self):
        error = UserIsNotActivated("User is not activated")
        assert str(error) == "User is not activated"
        assert isinstance(error, Exception)

    def test_refresh_token_not_found(self):
        error = RefreshTokenNotFound("Refresh token not found")
        assert str(error) == "Refresh token not found"
        assert isinstance(error, Exception)
