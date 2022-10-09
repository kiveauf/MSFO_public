#script to collect and analyze data from msfo sheets and real stock price

import PyPDF2
import tabula
import os
import requests

def get_file(url): # take url of the file
    global filename
    file = requests.get(url)
    filename = "MSFO.pdf"
    open(filename,'wb').write(file.content)
    print("Done")

def read_content(filename):
    _pdf = open(filename, 'rb')
    pdf_file = PyPDF2.PdfFileReader(_pdf)
    page_dohod = pdf_file.pages[9]
    info = page_dohod.extract_text()
    #print(info)
    for param in info.splitlines():
        if param.startswith("Прибыль за год") == True or param.startswith("Чистая прибыль") == True:
            info_pribyl = f"{param}"
            pribyl = param.split("  ")[1].lstrip()
            break
    print(info_pribyl, "необходимое число -", pribyl)
        
def analyze_data():
    pass

docs = ["https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf",
        "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf",
        "",
        ]

file_url = docs[1]

get_file(url = file_url)
read_content(filename = filename)
