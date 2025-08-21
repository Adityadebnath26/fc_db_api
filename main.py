from fastapi import FastAPI, Query
from pydantic import BaseModel
from db import get_connection
from quaries import select_from_table,select_by_name
from typing import Optional, Dict, Any
app = FastAPI()
class QueryInput(BaseModel):
    table: str
    columns: Optional[str] = "*"
    filters: Optional[Dict[str, Any]] = None

@app.get("/")
def root():
    return {"message": "Hello, API is running!"}

@app.post("/get_players/query")
def query_table(data: QueryInput):

    if list((data.filters).keys())[0]=="player_name" and data.table=="players":
        result=select_by_name((data.filters)["player_name"])
        return {"rows":result}
    else:
        result = select_from_table(
            table_name=data.table,
            filters=data.filters,
            columns=data.columns
        )
        return {"rows": result}