
class RecordNotFound(Exception):
    """Requested record in database was not found"""


class BadRequest(Exception):
    """Bad request"""


class PasswordsDontMatch(Exception):
    """Passwords don't match"""


class UserAlreadyExists(Exception):
    """User with given email address already exists"""


class UserIsNotActivated(Exception):
    """User with given email address is not activated"""


class RefreshTokenNotFound(Exception):
    """Raised when refresh token is not found in redis storage"""
