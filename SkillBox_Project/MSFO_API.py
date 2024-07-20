from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel

import MSFO_script

app = FastAPI()


class Ticker(BaseModel):
    url_to_pdf: Annotated[str, Query(min_length=1, pattern='\S+\.pdf')]
    ticker_name: Annotated[str, Query(pattern='^\w{1,4}$')]
    # parse_method: str


@app.get("/")
async def get_root():
    return "Welcome!"


@app.get("/MSFO/url")
def get_ticker_info_url(url_to_pdf: Annotated[str, Query(min_length=1, pattern='\S+\.pdf')]):
    info = MSFO_script.check_db_postsql_url(url_to_pdf)
    if info is None:
        return {"answer": "No data analyzed yet"}
    return {"answer": info}


@app.get("/MSFO/ticker")
def get_ticker_info_ticker(ticker_name: Annotated[str, Query(pattern='^\w{1,4}$')]):
    info = MSFO_script.check_db_postsql_ticker(ticker_name)
    if info is None:
        return {"answer": "No data analyzed yet"}
    return {"answer": info}


@app.post("/MSFO/")
def post_ticker_info(ticker_info: Ticker):
    url = ticker_info.url_to_pdf
    name = ticker_info.ticker_name
    # method = ticker_info.parse_method
    info = MSFO_script.run(url, name, "t")
    return {"answer": info}
