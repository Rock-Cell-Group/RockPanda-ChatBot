from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    user_name: str = Field(title="LINE帳號id")


class UserOut(BaseModel):
    id: int
    user_name: str = Field(title="LINE帳號id")

