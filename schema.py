from pydantic import BaseModel, Field


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
