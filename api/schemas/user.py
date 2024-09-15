from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserInSchema(BaseModel):
    first_name: constr(min_length=1, max_length=255)
    last_name: Optional[str] = None
    username: constr(min_length=1, max_length=255)
    email: EmailStr
    password: constr(min_length=6)


class UserOutSchema(BaseModel):
    id: int
    first_name: constr(min_length=1, max_length=255)
    last_name: Optional[str] = None
    username: constr(min_length=1, max_length=255)
    email: EmailStr

    class Config:
        from_attributes = True

