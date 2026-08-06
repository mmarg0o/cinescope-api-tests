from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from constants.roles import Roles
import datetime


class TestUser(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="Пароли должны совпадать")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    class Config:
        json_encoders = {
            Roles: lambda v: v.value
        }

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: Optional[bool] = None
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(BaseModel)("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

class Movies(BaseModel):
    id: int
    name: str
    imageUrl: str
    price: int
    description: str
    location: str
    published: bool
    genreId: int
    createdAt: Optional[str] = None
    rating: Optional[int] = None

    @field_validator("price")
    def price_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Цена должна быть больше 0")
        return value