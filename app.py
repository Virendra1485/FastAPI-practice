from fastapi import FastAPI
from item_route import item_router
from database import Base, engine
from models import *
Base.metadata.create_all(engine)
app = FastAPI()
secret_key = "sdfdjflksjflksdlfkjlk"
jwt_secret_key = "kjsdfklskdjf"
app.include_router(item_router, prefix="/v1")

