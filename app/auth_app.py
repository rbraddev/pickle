import base64
import pickle

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer

api = FastAPI()
auth = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

user_db = {
    "rreigns": {
        "password": "undisputed",
        "department": "bloodline"
    }
}


def get_token(credentials: HTTPBasicCredentials = Depends(auth)):
    user = user_db.get(credentials.username)
    if user and user["password"] == credentials.password:
        return {"user": User(credentials.username, user["department"])}	
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

@api.get("/token")
def token(token: dict[str, User] = Depends(get_token)):
    return base64.b64encode(pickle.dumps(token, protocol=0))

@api.get("/current_user")
def get_user_details(token: str = Depends(oauth2_scheme)):
    try:
        user = pickle.loads(base64.b64decode(token))
    except pickle.UnpicklingError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if user_detail := user.get("user"):
        return {"data": {
            "username": user_detail.username,
            "department": user_detail.department
        }}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@api.get("/")
async def root():
    return {"message": "Pickle"}
