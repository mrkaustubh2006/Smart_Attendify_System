"""
services/validation.py
Server-side validation and sanitization for authentication forms.
"""

import re
import bleach
from pydantic import BaseModel, EmailStr, Field, field_validator


def sanitize_text(value: str) -> str:
    """Remove HTML tags, scripts, and dangerous characters."""
    value = bleach.clean(value or "", tags=[], strip=True)
    value = re.sub(r"[<>\'\"`;]", "", value)
    return value.strip()


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value):
        value = sanitize_text(str(value)).lower()

        if len(value) > 254:
            raise ValueError("Invalid input")

        return value

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value):
        value = sanitize_text(str(value))

        if not (8 <= len(value) <= 128):
            raise ValueError("Invalid input")

        return value


class RegisterSchema(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    student_id: str = Field(min_length=1, max_length=64)
    class_name: str = Field(min_length=1, max_length=64)
    roll_no: str = Field(min_length=1, max_length=20)
    department: str | None = None

    @field_validator(
        "name",
        "student_id",
        "class_name",
        "roll_no",
        "department",
        mode="before",
    )
    @classmethod
    def sanitize_fields(cls, value):
        if value is None:
            return None

        value = sanitize_text(str(value))

        if len(value) > 100:
            raise ValueError("Invalid input")

        return value

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, value):
        value = sanitize_text(str(value)).lower()

        if len(value) > 254:
            raise ValueError("Invalid input")

        return value

    @field_validator("password", mode="before")
    @classmethod
    def sanitize_password(cls, value):
        value = sanitize_text(str(value))

        if not (8 <= len(value) <= 128):
            raise ValueError("Invalid input")

        return value
