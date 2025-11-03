from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegistrationSchema(BaseModel):
    password: str
    password2: str
    email: EmailStr

    @field_validator('password', 'password2')
    @classmethod
    def validate_password_length(cls, v):
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        return v


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        return v


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = False
    is_superuser: bool = False
    created: datetime | None = None
    last_login: datetime | None = None
    confirmed: bool = False


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        return v


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class MessageSchema(BaseModel):
    message: str


# Create instances of schemas for compatibility with existing code structure
class Schemas:
    registration = RegistrationSchema
    login = LoginSchema
    user_create = UserCreate
    user_response = UserResponse
    token = TokenSchema
    refresh_token = RefreshTokenSchema
    message = MessageSchema


schemas = Schemas()
