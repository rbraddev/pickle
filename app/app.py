import base64
import pickle

from fastapi import FastAPI, Request, Response, Body, HTTPException, status
from fastapi.responses import JSONResponse

from models import Session, Basket


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

EXCLUDED_MIDDLEWARE_ROUTES = ["/items"]


def add_items_to_basket(basket: Basket, item: str, qty: int):
    if not ITEMS_DB.get(item):
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid item: {item}")
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
    if request.scope["path"] not in EXCLUDED_MIDDLEWARE_ROUTES and not request.headers.get("X-Session"):
        response = JSONResponse(content={"data": "Session Created"})
        response.headers["X-Session"] = create_session()
    else:
        response = await call_next(request)
    return response


@api.get("/items")
def get_items():
    return {"data": {"items": ITEMS_DB}}


@api.post("/basket", status_code=201)
def add_items(request: Request, response: Response, items: list[dict] = Body()):
    session = load_session(request.headers["X-Session"])
    for item in items:
        add_items_to_basket(session.basket, item.get("id"), item.get("qty"))
    response.headers["X-Session"] = pickle_session(session)
    return {"data": "items added to basket"}


@api.get("/basket")
def get_basket(request: Request, response: Response):
    session = load_session(request.headers["X-Session"])
    response.headers["X-Session"] = request.headers["X-Session"]
    return {"data": {"items": session.basket.items}}


@api.get("/")
async def root():
    return {"message": "Pickle"}
