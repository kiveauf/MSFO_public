from fastapi import FastAPI
from pydantic import BaseModel

import MSFO_script

app = FastAPI()

class Ticker(BaseModel):
    url_to_pdf: str
    ticker_name: str
    #parse_method: str


@app.get("/")
async def get_root():
    return "Welcome!"


@app.get("/MSFO/url")
async def get_ticker_info_url(url_to_pdf : str):
    info = MSFO_script.check_db_postsql_url(url_to_pdf)
    if info == None:
        return {"answer": "No data analyzed yet"}
    return {"answer" : info}


@app.get("/MSFO/ticker")
async def get_ticker_info_ticker(ticker_name : str):
    info = MSFO_script.check_db_postsql_ticker(ticker_name)
    if info == None:
        return {"answer": "No data analyzed yet"}
    return {"answer" : info}


@app.post("/MSFO/")
def post_ticker_info(ticker_info : Ticker):
    url = ticker_info.url_to_pdf
    name = ticker_info.ticker_name
    #method = ticker_info.parse_method
    info = MSFO_script.run(url, name, "t")
    return {"answer" : info}  

                             

                             
