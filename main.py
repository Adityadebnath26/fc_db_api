from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

from db import get_connection
from quaries import select_from_table, select_by_name, purchase, cancel_purchase, select_by_id
from dotenv import load_dotenv
load_dotenv()

# ---------------------
# App Setup
# ---------------------
app = FastAPI()

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY")   # 👉 change this to something strong
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 8))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ---------------------
# Dummy Users & Clients
# ---------------------
fake_users = {
    os.getenv("ADMIN_USERNAME"): {
        "username": os.getenv("ADMIN_USERNAME"),
        "password": os.getenv("ADMIN_PASSWORD")
    }
}

fake_clients = {
    os.getenv("CLIENT_ID"): {"client_secret": os.getenv("CLIENT_SECRET")},
    os.getenv("ANOTHER_CLIENT_ID"): {"client_secret": os.getenv("ANOTHER_CLIENT_SECRET")}
}

# ---------------------
# Models
# ---------------------
class QueryInput(BaseModel):
    table: str
    columns: Optional[str] = "*"
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

class PurchaseRequest(BaseModel):
    player_id: int
    manager_id: int
    amount: float

class CancelRequest(BaseModel):
    purchase_id: int   

# ---------------------
# Auth Helpers
# ---------------------
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return subject
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ---------------------
# Auth Routes
# ---------------------
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ Human login with username & password """
    user = fake_users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/client-login")
def client_login(client_id: str = Form(...), client_secret: str = Form(...)):
    """ Machine-to-machine login with client_id & client_secret """
    client = fake_clients.get(client_id)
    if not client or client["client_secret"] != client_secret:
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": f"client:{client_id}"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------
# Public Route
# ---------------------
@app.get("/")
def root():
    return {"message": "Hello, API is running!"}

# ---------------------
# Protected Routes
# ---------------------
@app.post("/players")
def query_table(data: QueryInput):
    result = select_from_table(
        table_name=data.table,
        filters=data.filters,
        columns=data.columns,
        limit=data.limit,
        offset=data.offset
    )
    return {"rows": result}

@app.get("/players_name/{name}")
def get_players_by_name(name: str):
    result = select_by_name(name)
    return {"rows": result}

@app.get("/players_id/{id}")
def get_players_by_id(id: int):
    result = select_by_id(id)
    return {"rows": result}





@app.post("/purchase_record")
def purchase_record(player_id: int, manager_id: int, amount: float, user: str = Depends(get_current_user)):
    try:
        purchase_id = purchase(player_id, manager_id, amount)  # call from quaries.py
        return {
            "message": "Purchase successful",
            "purchase_id": purchase_id,
            "requested_by": user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")
    

@app.post("/cancel_purchase_record")
def cancel_purchase_record(purchase_id: int, user: str = Depends(get_current_user)):
    """
    Cancel a purchase (using quaries.py)
    """
    try:
        result = cancel_purchase(purchase_id)  # call from quaries.py
        if not result:
            raise HTTPException(status_code=404, detail="Purchase not found or could not be cancelled")

        return {
            "message": f"Purchase {purchase_id} cancelled successfully",
            "requested_by": user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancel failed: {str(e)}")




