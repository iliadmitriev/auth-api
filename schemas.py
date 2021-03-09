from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models import User


class RegisterUserSchema(Schema):
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


class LoginUserSchema(Schema):
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


class RegisteredUser(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)


class UserSchema(SQLAlchemyAutoSchema):
    """
    id = fields.Integer(dump_only=True)
    email = fields.String(
        required=True,
        validate=validate.Email()
    )
    is_active = fields.Boolean()
    is_superuser = fields.Boolean()
    created = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    """
    class Meta:
        model = User

    id = auto_field(dump_only=True)
    created = auto_field(dump_only=True)
    password = auto_field(dump_only=True)
    email = auto_field(
        'email',
        validate=validate.Email()
    )


class TokenSchema(Schema):
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)


class RefreshTokenSchema(Schema):
    refresh_token = fields.String(required=True)


class Message(Schema):
    message = fields.String(
        dump_only=True,
        required=True
    )


register_user_schema = RegisterUserSchema()
login_user_schema = LoginUserSchema()
registered_user_schema = RegisteredUser()
user_schema = UserSchema()
user_schema_partial = UserSchema(partial=True)
users_schema = UserSchema(many=True)
token_schema = TokenSchema()
refresh_token_schema = RefreshTokenSchema()
message_schema = Message()
