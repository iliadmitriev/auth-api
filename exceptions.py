
class NotFound(Exception):
    """Object was not found general Exception"""


class RecordNotFound(NotFound):
    """Requested record in database was not found"""


class RefreshTokenNotFound(NotFound):
    """Raised when refresh token is not found in redis storage"""


class BadRequest(Exception):
    """Bad request"""


class PasswordsDontMatch(BadRequest):
    """Passwords don't match"""


class UserAlreadyExists(BadRequest):
    """User with given email address already exists"""


class UserIsNotActivated(Exception):
    """User with given email address is not activated"""
