from marshmallow import Schema, fields, validate


class RegisterUser(Schema):
    password = fields.String(
        required=True,
        validate=validate.Length(max=100)
    )
    password2 = fields.String(
        required=True,
        validate=validate.Length(max=100)
    )
    email = fields.String(
        required=True,
        validate=validate.Email()
    )

    class Meta:
        strict = True


class LoginUser(Schema):
    email = fields.String(
        required=True,
        validate=validate.Email()
    )
    password = fields.String(
        required=True,
        validate=validate.Length(max=100)
    )

    class Meta:
        strict = True


class User(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)


class Token(Schema):
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)


class RefreshToken(Schema):
    refresh_token = fields.String(required=True)


class Message(Schema):
    message = fields.String(
        dump_only=True,
        required=True
    )


register_user_schema = RegisterUser()
login_user_schema = LoginUser()
user_schema = User()
token_schema = Token()
message_schema = Message()
