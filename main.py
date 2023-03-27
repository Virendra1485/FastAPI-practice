from fastapi import FastAPI, status, Body, Cookie, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Union
from typing_extensions import Annotated
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello welcome to you"}


@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
async def path_param(item_id: str):
    """
    This end-point describe the path parameter with status code and Json response as well as description
    """
    # return {"item_id": item_id}
    return JSONResponse(content={"item_id": item_id})


# @app.get("/items/", status_code=status.HTTP_200_OK)
# async def query_param(q: Optional[str] = None):
#     """
#     This end-point describe the query parameter
#     as well as use optional for less version of python 3.10
#     """
#     return JSONResponse(content={"q": q})


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    # description: str | None = None  This syntax used python version 3.10
    price: int
    tax: float

    class Config:
        """
        This config class is a sample payload for swagger.
        """
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 16.25,
                "tax": 1.67,
            }
        }


@app.post("/get_item/", response_model=Item)
async def get_item(item: Item):
    """
    This endpoint describe the payload class with response class
    """
    return JSONResponse(content=item.dict())


@app.post("/item_params/{item_id}/", response_model=List[Dict[str, Union[str, Item]]])
async def item_params(item_id: str, item: Item, tags: Optional[str] = None):
    """
    This payload describe the path param, query param and payload
    Also describe the use of response_model with type of response
    Dict accept two arguments type of keys and types of value
    """
    data = {"item_id": item_id, "item": item.dict(), "tags": tags}
    return JSONResponse(content=[data])


class Offer(BaseModel):
    """
    This class describe the nested Class uses
    ... indicate that this field is required
    alias used for public name
    gt and lt stands for greater than and less than
    """
    name: str = Field(..., max_length=10, min_length=5, alias="Offer name")
    description: str
    price: int = Field(gt=0, lt=10000)
    items: Optional[List[Item]] = None


@app.post("/offer/", response_model=Offer)
async def offers(offer: Offer):
    return JSONResponse(content=offer.dict())


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item = Body(
        ...,
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "A __normal__ item works _correctly_",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 16.25,
                    "tax": 1.67,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {"name": "Bar", "price": "16.25"},
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "description": "Hello youtubers",
                "value": {"name": "Baz", "price": "sixteen point two five"},
            },
        },
    ),
):
    """
    This endpoint describe that we can show multiple examples
    """
    results = {"item_id": item_id, "item": item}
    return results


@app.get("/items/")
def read_items(ads_id: Annotated[Union[str, None], Cookie()] = None):
    """
    Use of Cookie same we can use Header as well.
    No extra path or query parameter add in URL.
    """
    return {"ads_id": ads_id}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    """
    UploadFile, on the other hand, is a class that represents an uploaded file in the context of an HTTP request.
    """
    return {"filename": file.filename}


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    """
    In this function File used as a type hint for a file like object in request body.
    """
    return {"file_size": len(file)}


@app.post("/file_many/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    """
    In this endpoint we can use Form and File in a single request.
    """
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

items = {"foo": "The Foo Wrestlers"}


@app.get("/items_error/{item_id}", status_code=status.HTTP_200_OK)
async def read_item(item_id: str):
    """
    Here we can raise exception.
    """
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"item": items[item_id]}
