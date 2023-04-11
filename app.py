import time

from fastapi import FastAPI, Request, WebSocket
from item_route import item_router
from database import engine
from models import *
from item_route import product_router
from fastapi_utils.tasks import repeat_every
Base.metadata.create_all(engine)
app = FastAPI()
secret_key = "sdfdjflksjflksdlfkjlk"
jwt_secret_key = "kjsdfklskdjf"
app.include_router(item_router, prefix="/v1")
app.include_router(product_router, prefix="/v2")


@app.on_event("startup")
@repeat_every(seconds=100)
def print_user_greetings():
    print("Hii user")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response



