from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi_mail import MessageSchema
from sqlalchemy.orm import Session
from database import get_db
from models import Item
from schema import ItemSchema, ItemCreateSchema
from config import fast_mail


item_router = APIRouter(tags=["item"])


@item_router.get("/test_router")
async def test():
    return {"hello": "hello"}


async def back_task(hello: str, tata: str):
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
        recipients=["virendrasinghrawat3112@gmail.com"],  # List of recipients, as many as you can pass
        body=template,
        subtype="html"
    )
    await fast_mail.send_message(message)
    print(hello, tata)


@item_router.get("/items/", response_model=List[ItemSchema], status_code=status.HTTP_200_OK)
async def read_items(background_task: BackgroundTasks, db: Session = Depends(get_db)):
    background_task.add_task(back_task, "hello", "tata")

    items = db.query(Item).all()
    return items


@item_router.post("/items/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreateSchema, db: Session = Depends(get_db)):
    item_instance = Item(item.dict())
    db.add(item_instance)
    db.commit()
    db.refresh(item_instance)
    return item_instance


@item_router.get("/item/{item_id}", response_model=ItemSchema, status_code=status.HTTP_200_OK)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not Found")
    return item


@item_router.patch("/item/{item_id}", response_model=ItemSchema, status_code=status.HTTP_200_OK)
async def update_item(item_id: int, item: ItemCreateSchema,  db: Session = Depends(get_db)):
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
async def delete_item(item_id: int,  db: Session = Depends(get_db)):
    instance = db.query(Item).filter(Item.id == item_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Item not Found")

    db.delete(instance)
    db.commit()
    return {"message": "Item deleted successfully"}
