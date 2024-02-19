from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserValidator(BaseModel):
    username : str = Field(max_length=15,min_length=3)
    password : str
    email : EmailStr
    location : Optional[str]=None

    @field_validator('password')
    @classmethod
    def validate_password(cls,value):
        password_pattern=r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&]).{8,}$'
        if re.match(password_pattern,value):
            return value
        raise ValueError(f'Password must contain a special character and uppercase letter')