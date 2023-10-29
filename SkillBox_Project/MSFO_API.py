from fastapi import FastAPI
from pydantic import BaseModel
import MSFO_script

app = FastAPI()

class Ticker(BaseModel):
    url_to_pdf: str
    ticker_name: str
    #parse_method: str


@app.get("/MSFO/")
async def get_ticker_info(ticker_name : str):
    info = MSFO_script.read_db_postsql(ticker_name)
    if info == None:
        return {"answer": "No data analyzed yet"}
    return {"answer" : info}


@app.post("/MSFO/")
def post_ticker_info(ticker_info : Ticker):
    url = ticker_info.url_to_pdf
    name = ticker_info.ticker_name
    #method = ticker_info.parse_method
    info = MSFO_script.run(url, name, method = "p")
    return {"answer" : info}  

                             

                             
