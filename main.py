from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel


app = FastAPI()


@app.get('/getHealth')
def health():
    return {"Status" : "OK"}

