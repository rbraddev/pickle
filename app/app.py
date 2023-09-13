import base64
import pickle

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders

from models import Session, Basket, Item


api = FastAPI()

ITEMS_DB = {
    "0001": {
        "name": "Rasberry Pi",
        "price": 60
    },
    "0002": {
        "name": "SD Card",
        "price": 15
    },
    "0003": {
        "name": "HDMI Cable",
        "price": 10
    }
}

EXCLUDED_MIDDLEWARE_ROUTES = ["/items", "/docs", "/"]


def add_items_to_basket(basket: Basket, item: str, qty: int):
    if not ITEMS_DB.get(item):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid item: {item}")
    if basket.items.get(item):
        basket.items[item]["qty"] += qty
    else:
        basket.items.update({
            item: {
                "qty": qty
            }
        })


def create_session() -> str:
    return base64.b64encode(pickle.dumps({"session": Session(basket=Basket())})).decode()


def pickle_session(session: Session) -> str:
    return base64.b64encode(pickle.dumps({"session": session})).decode()


def load_session(pickled_session: str) -> Session:
    try:
        return pickle.loads(base64.b64decode(pickled_session))["session"]
    except pickle.UnpicklingError:
        raise HTTPException(status_code=status.HTTP_400_UNAUTHORIZED, detail="Invalid Session")


@api.middleware("http")
async def check_session(request: Request, call_next) -> JSONResponse:
    if request.scope["path"] not in [route.path for route in api.routes]:
        response = JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Item not found")
    elif not request.headers.get("X-Session"):
        headers_copy = MutableHeaders(request._headers)
        headers_copy["X-Session"] = create_session()
        request._headers = headers_copy
        request.scope.update(headers=request.headers.raw)
        response = await call_next(request)
    else:
        reponse = await call_next(request)
    return response


@api.get("/items")
def get_items():
    return {"data": {"items": ITEMS_DB}}


@api.put("/basket", status_code=status.HTTP_201_CREATED)
def add_items(request: Request, response: Response, item: Item):
    session = load_session(request.headers["X-Session"])
    add_items_to_basket(session.basket, item.id, item.qty)
    response.headers["X-Session"] = pickle_session(session)
    return {"data": "item added to basket"}


@api.get("/basket")
def get_basket(request: Request, response: Response):
    session = load_session(request.headers["X-Session"])
    response.headers["X-Session"] = request.headers["X-Session"]
    return {"data": {"items": session.basket.items}}


@api.get("/")
async def root():
    return {"message": "Visit the docs at http://127.0.0.1:8000/docs"}
