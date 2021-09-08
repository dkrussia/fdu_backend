from typing import Optional, List, Dict

from pydantic import (
    BaseModel, Field,
    # EmailStr,
)


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    # email: Optional[EmailStr] = None
    # is_active: Optional[bool] = True
    # full_name: Optional[str] = None

class User(BaseModel):
    id: str = Field(
        title = 'ID'
    )
    username: str = Field(
        title = 'Имя пользователя'
    )
    email: str = Field(
        title = 'Электронная почта'
    )

    class Config:
        orm_mode = True

class UserForm(BaseModel):
    username: str = Field(
        title = 'Имя пользователя'
    )
    email: str = Field(
        title = 'Электронная почта'
    )

    class Config:
        orm_mode = True

class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password: str
    email: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    username: str
    email: str


class UserList(BaseModel):
    users: List[User]

