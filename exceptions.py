
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

