from schemas.users import Message

responses_default = {
    401: {
        "description": "Unauthorized user response",
        "schema": Message(),
        "examples": {
            "No authorization": {"message": "HTTPUnauthorized: Authorization required"},
            "Expired token": {"message": "HTTPUnauthorized: Invalid authorization token, Signature has expired"}
        }
    },
    403: {
        "description": "HTTPForbidden: Invalid authorization header",
        "schema": Message(),
        "examples": {
            "Invalid token": {"message": "HTTPForbidden: Invalid authorization header"},
            "Not enough privileges": {"message": "HTTPForbidden: Insufficient scopes"}
        }
    },
    500: {"description": "Server error"},
}

response_400 = {
    400: {
        "description": "Response to all bad, malformed, unvalidated request",
        "schema": Message(),
        "examples": {
            "Duplicated key or id": {"message": "BadRequest: duplicate key value violates unique constraint"},
            "Validation errors": {"message": "ValidationError: {'email': ['Not a valid email.']}"}
        }
    }
}

response_404 = {
    404: {
        "description": "RecordNotFound: Profile with user_id=%d is not found",
        "schema": Message(),
        "examples": {
            "Record not found": {"message": "RecordNotFound: Profile with user_id=%d is not found"}
        }
    }
}
