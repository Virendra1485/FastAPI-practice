from sqlalchemy import Column, String, Integer
from database import Base


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)

    def __init__(self, data):
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
