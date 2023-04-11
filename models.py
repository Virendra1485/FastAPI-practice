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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    def __init__(self, data):
        self.email = data.get("email")
        self.password = data.get("password")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)

    def __init__(self, data):
        self.name = data.get("name")
        self.category = data.get("category")
