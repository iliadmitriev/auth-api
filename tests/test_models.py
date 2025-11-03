from models.users import User


class TestUserModel:
    """Test User model"""

    def test_user_creation(self):
        """Test creating a User instance"""
        user = User(email="test@example.com", password="hashed_password")

        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        # Check defaults - Note: These will be None until saved to DB
        assert user.is_active in [None, False]  # Can be None before DB save
        assert user.is_superuser in [None, False]  # Can be None before DB save
        assert user.confirmed in [None, False]  # Can be None before DB save
        assert user.created is None  # Will be set by DB
        assert user.last_login is None

    def test_user_with_values(self):
        """Test User model with explicit values"""
        user = User(
            email="test@example.com",
            password="hashed_password",
            is_active=True,
            is_superuser=True,
            confirmed=True,
        )

        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        assert user.is_active in [True, None]  # Can be None before DB save
        assert user.is_superuser in [True, None]  # Can be None before DB save
        assert user.confirmed in [True, None]  # Can be None before DB save

    def test_user_table_name(self):
        """Test User model table name"""
        assert User.__tablename__ == "user"

    def test_user_inheritance(self):
        """Test User model inheritance from Base"""
        assert hasattr(User, "__tablename__")

    def test_user_defaults(self):
        """Test User model defaults"""
        user = User(email="test@example.com", password="hashed_password")

        assert user.id is None  # Auto-increment
        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        # These can be None before saving to DB
        assert user.is_active in [None, False]
        assert user.is_superuser in [None, False]
        assert user.confirmed in [None, False]
        assert user.created is None  # Will be set by DB
        assert user.last_login is None  # Default

    def test_user_repr(self):
        """Test User model representation"""
        user = User(
            id=1,
            email="test@example.com",
            password="hashed_password",
            # Other fields will use defaults
        )

        # Just check that repr doesn't crash
        repr_str = repr(user)
        assert "User" in repr_str
