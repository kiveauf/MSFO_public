#script to collect and analyze data from msfo sheets and real stock price

import PyPDF2
import tabula
import os
import requests

class Ticker():
    def _init_(self):
        self.ticker_name = str()
        self.pribyl = 0
        self.viruchka = int()
        self.stock_price = int()

def get_file(tkr, url): # take url of the file
    global filename
    file = requests.get(url)
    tkr.ticker_name = "ticker"#input("Type ticker: ")
    filename = f"{tkr.ticker_name}_MSFO.pdf"
    open(filename,'wb').write(file.content)
    print("Done")

def edit_data(text):
    clear_text = str()
    full_stroka = str()
    condition = True
    for stroka in text.splitlines():
        #stroka = stroka.strip("  ")
        if len(stroka.strip()) == 0 or stroka == "\n":
          #  print(f"eto stroka - {stroka}a eto dlina {len(stroka)}")
            stroka = stroka.strip(" \n")
            continue
        if stroka[0].isupper() == True:
            clear_text += "\n"
         #   print(f"eto stroka - {stroka}a eto dlina {len(stroka)}")
        clear_text += stroka + " "
    return clear_text

    

def read_content(tkr, filename):
    info_pribyl = "No data"
    _pdf = open(filename, 'rb')
    pdf_file = PyPDF2.PdfFileReader(_pdf, strict=False)
    page_dohod = pdf_file.pages[24]
    info = page_dohod.extract_text()
    info = edit_data(text = info)
    print(info)
    #for param in info.splitlines():
    #    if param.startswith("Прибыль за год") == True or param.startswith("Чистая прибыль") == True:
    #        info_pribyl = f"{param}"
    #        tkr.pribyl = param.split("  ")[1].lstrip()
    #        break
    #print(info_pribyl, "необходимое число -", tkr.pribyl)
        
def analyze_data():
    pass

docs = ["https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf",
        "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf",
        "https://acdn.tinkoff.ru/static/documents/223e5d7f-6d12-429f-aae1-a25b154ea3e2.pdf",
        ]

file_url = docs[2]
ticker = Ticker()

get_file(tkr = ticker, url = file_url)
read_content(tkr = ticker, filename = filename)

