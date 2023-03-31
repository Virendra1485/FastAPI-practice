from pydantic import BaseModel, Field, EmailStr, SecretStr


class ItemCreateSchema(BaseModel):
    title: str = Field(...)
    description: str = Field(...)

    class Config:
        orm_mode = True


class ItemSchema(ItemCreateSchema):
    id: int = Field(..., gt=0)

    class Config:
        """
        This is used to instruct Pydantic to read the data from ORM objects.
        """
        orm_mode = True


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: SecretStr

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

