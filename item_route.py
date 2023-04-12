import jwt
import time
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    BackgroundTasks,
    Request,
    WebSocket,
)
from fastapi_mail import MessageSchema
from sqlalchemy.orm import Session
from database import get_db
from models import Item, User, Product
from schema import (
    ItemSchema,
    ItemCreateSchema,
    UserCreateSchema,
    UserSchema,
    TokenSchema,
    ProductSchema,
    ProductCreateSchema,
)
from config import fast_mail
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

item_router = APIRouter(tags=["Item"])
product_router = InferringRouter(tags=["Products"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        import app

        isTokenValid: bool = False

        try:
            decoded_token = jwt.decode(
                jwt_token, app.jwt_secret_key, algorithms=["HS256"]
            )
            if decoded_token.get("exp") >= time.time():
                isTokenValid = True
                return isTokenValid
            else:
                return isTokenValid
        except:
            return isTokenValid


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    import app

    payload = jwt.decode(token, app.jwt_secret_key, algorithms="HS256")
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return user


@item_router.get("/test_router")
def test():
    return {"hello": "hello"}


def back_task(hello: str, tata: str):
    template = """
                <html>
                <body>


        <p>Hi !!!
                <br>Thanks for using fastapi mail, keep using it..!!!</p>


                </body>
                </html>
                """
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[
            "virendrasinghrawat3112@gmail.com"
        ],  # List of recipients, as many as you can pass
        body=template,
        subtype="html",
    )
    fast_mail.send_message(message)
    print(hello, tata)


@item_router.get(
    "/items/",
    response_model=List[ItemSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(JWTBearer())],
)
def read_items(background_task: BackgroundTasks, db: Session = Depends(get_db)):
    background_task.add_task(back_task, "hello", "tata")
    items = db.query(Item).all()
    return items


@item_router.post(
    "/items/",
    response_model=ItemSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(JWTBearer())],
)
def create_item(item: ItemCreateSchema, db: Session = Depends(get_db)):
    item_instance = Item(item.dict())
    db.add(item_instance)
    db.commit()
    db.refresh(item_instance)
    return item_instance


@item_router.get(
    "/item/{item_id}", response_model=ItemSchema, status_code=status.HTTP_200_OK
)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not Found")
    return item


@item_router.patch(
    "/item/{item_id}", response_model=ItemSchema, status_code=status.HTTP_200_OK
)
def update_item(item_id: int, item: ItemCreateSchema, db: Session = Depends(get_db)):
    instance = db.query(Item).filter(Item.id == item_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Item not Found")
    for key, value in item.dict().items():
        setattr(instance, key, value)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@item_router.delete("/item/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    instance = db.query(Item).filter(Item.id == item_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Item not Found")

    db.delete(instance)
    db.commit()
    return {"message": "Item deleted successfully"}


@item_router.post(
    "/user/sign_up", status_code=status.HTTP_201_CREATED, response_model=UserSchema
)
def user_create(user: UserCreateSchema, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="User already exist")
    user_instance = User(user.dict())
    user_instance.password = bcrypt.hash(user.password._secret_value)
    db.add(user_instance)
    db.commit()
    db.refresh(user_instance)
    return user_instance


def create_access_token(data: dict) -> str:
    import app

    expire = datetime.utcnow() + timedelta(hours=15)
    data.update({"exp": expire})
    access_token = jwt.encode(data, app.jwt_secret_key, algorithm="HS256")
    return access_token


def create_refresh_token(data: dict) -> str:
    import app

    expire = datetime.utcnow() + timedelta(days=1)
    data.update({"exp": expire})
    refresh_token = jwt.encode(data, app.jwt_secret_key, algorithm="HS256")
    return refresh_token


@item_router.post(
    "/user/sign_in", status_code=status.HTTP_200_OK, response_model=TokenSchema
)
def user_sign_in(user: UserCreateSchema, db: Session = Depends(get_db)):
    user_instance = db.query(User).filter(User.email == user.email).first()
    if not user_instance:
        raise HTTPException(status_code=400, detail="User not found.")
    if not bcrypt.verify(user.password._secret_value, user_instance.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    access_token = create_access_token({"sub": user_instance.email})
    refresh_token = create_refresh_token({"sub": user_instance.email})
    return {"access_token": access_token, "refresh_token": refresh_token}


@cbv(product_router)
class ProductCbv:
    db: Session = Depends(get_db)

    @product_router.get(
        "/product_get",
        response_model=List[ProductSchema],
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(JWTBearer())],
    )
    def get_all_product(self):
        product = self.db.query(Product).all()
        return product

    @product_router.post(
        "/product",
        response_model=ProductSchema,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(JWTBearer())],
    )
    def post(self, product: ProductCreateSchema):
        product_instance = Product(product.dict())
        self.db.add(product_instance)
        self.db.commit()
        self.db.refresh(product_instance)
        return product_instance

    @product_router.get(
        "/product/{product_id}",
        response_model=ProductSchema,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(JWTBearer())],
    )
    def get(self, product_id: int):
        product = self.db.query(Product).get(product_id)
        if product:
            return product
        raise HTTPException(status_code=404, detail="Product not found")

    @product_router.patch(
        "/product/{product_id}",
        response_model=ProductSchema,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(JWTBearer())],
    )
    def update_product(self, product_id: int, product: ProductCreateSchema):
        instance = self.db.query(Product).get(product_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Product not Found")
        for key, value in product.dict().items():
            setattr(instance, key, value)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    @product_router.delete(
        "/product/{product_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(JWTBearer())],
    )
    def delete_item(self, product_id: int):
        instance = self.db.query(Product).get(product_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Product not Found")

        self.db.delete(instance)
        self.db.commit()
        return {"message": "Item deleted successfully"}


@item_router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Your Response -------------{data}")
        await websocket.close()
