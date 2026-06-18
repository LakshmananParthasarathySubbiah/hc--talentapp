from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from typing import Optional
import re

EMAIL_RE    = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,32}$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")

class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v: str) -> str:
        v = v.strip()
        if not USERNAME_RE.match(v):
            raise ValueError("Username must be 3–20 characters: letters, numbers, underscores only.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("Enter a valid email address.")
        if len(v) > 120:
            raise ValueError("Email must be under 120 characters.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        if not PASSWORD_RE.match(v):
            raise ValueError("Password must be 8–32 chars and include at least one uppercase letter, one number, and one special character.")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self) -> 'RegisterSchema':
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self

class LoginSchema(BaseModel):
    identifier: str
    password: str

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Email or username is required.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("Password is required.")
        return v

class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not PASSWORD_RE.match(v):
            raise ValueError("Password must be 8–32 chars and include at least one uppercase letter, one number, and one special character.")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self) -> 'ChangePasswordSchema':
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self

class ProfileSchema(BaseModel):
    bio: str
    skills: str
    github: Optional[str] = ""
    linkedin: Optional[str] = ""
    website: Optional[str] = ""

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Biography is required.")
        if len(v) > 500:
            raise ValueError("Biography must be under 500 characters.")
        return v

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Please list at least one skill.")
        return v

    @field_validator("github", "linkedin", "website")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return ""
        v = v.strip()
        if v == "":
            return ""
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError("Enter a valid URL.")
        return v

def format_pydantic_errors(e: ValidationError) -> dict:
    errors = {}
    for err in e.errors():
        loc = err['loc']
        msg = err['msg']
        
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
            
        if loc:
            field = str(loc[-1])
            if field in ("__root__", "None", ""):
                errors["confirm_password"] = msg
            else:
                errors[field] = msg
        else:
            errors["confirm_password"] = msg
    return errors
