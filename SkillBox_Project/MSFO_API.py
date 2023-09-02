from fastapi import FastAPI
from pydantic import BaseModel
import MSFO_script

app = FastAPI()

class Ticker(BaseModel):
    url_to_pdf: str
    ticker_name: str
    parse_method: str


@app.post("/MSFO/")
def get_ticker_info(ticker_info : Ticker):
    url = ticker_info.url_to_pdf
    name = ticker_info.ticker_name
    method = ticker_info.parse_method
    info = MSFO_script.run(url, name, method)
    return info
                             
