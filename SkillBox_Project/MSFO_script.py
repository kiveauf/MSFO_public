#script to collect and analyze data from msfo sheets and real stock price

import PyPDF2
import requests
import logging
import time



logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.CRITICAL)

class Ticker():
    def _init_(self):
        self.ticker_name = str()
        self.pribyl = 0
        self.viruchka = 0
        self.stock_price = int()

def get_file(tkr, url): # take url of the file
    file = requests.get(url)
    tkr.ticker_name = "ticker" #input("Type ticker: ")
    filename = f"{tkr.ticker_name}_MSFO.pdf"
    open(filename,'wb').write(file.content)
    print("Done")
    return filename

def edit_data(text): #takes whole str doc and return list of str
    global measure_unit
    clear_text = str()
    stroki = list()
    if len(check(text)) == 0:
        return []
    for stroka in text.splitlines():
        if len(stroka.strip()) == 0 or stroka == "\n":
            stroka = stroka.strip(" \n")
            continue
        if stroka[0].isupper() == True:
            clear_text = edit_whitespaces(clear_text)
            stroki.append(clear_text)
            clear_text = ""
        clear_text += stroka + " "
        for word in stroka.split():
            if word in ["тыс.", "тыс", "тысячах", "thousands"]:
                measure_unit = 1000 #measuring unit
            if word in ["млн.", "млн", "миллионах", "millions"]:
                measure_unit = 1000000 #measuring unit
    return stroki

def edit_whitespaces(clear_text): # clearing line of text
    c_t = str()
    while clear_text.count("  ") != 0:
        whitespaces = clear_text.find("  ")
        if (whitespaces - 1 >= 0) and (whitespaces + 2 < len(clear_text)):
            if clear_text[whitespaces - 1].isdigit() == False and clear_text[whitespaces + 2].isdigit() == False:
                clear_text = clear_text.replace("  ", " ", 1)
            else:
                break
        elif (whitespaces == 0) and (whitespaces + 2 < len(clear_text)):
            if clear_text[whitespaces + 2].isdigit() == False:
                clear_text = clear_text.replace("  ", " ", 1)
            else:
                break
        elif (whitespaces - 1 >= 0) and (whitespaces + 2 == len(clear_text) - 1):
            if clear_text[whitespaces - 1].isdigit() == False:
                clear_text = clear_text.replace("  ", " ", 1)
            else:
                break
        else:
            break
    for i in range(len(clear_text) - 1):
        if clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1] == ",":
           continue
        if clear_text[i] == " " and clear_text[i+1] == "/" and clear_text[i-1].isalpha() == True:
           continue
        if clear_text[i] == " " and clear_text[i-1] == "/" and clear_text[i+1].isalpha() == True:
           continue
        if clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "/":
           continue
        if clear_text[i] == " " and clear_text[i-1] == "/" and clear_text[i+1] == "(":
           continue
        if clear_text[i] == " " and clear_text[i-1] == "(" and clear_text[i+1].isalpha() == True:
           continue
        if clear_text[i] == " " and clear_text[i+1] == ")" and clear_text[i-1].isalpha() == True:
           continue
        c_t += clear_text[i]
        if clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1] == "(" and clear_text[i+2].isdigit() == True:
           c_t += " "
        elif clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1].isdigit() == True:
           c_t += " "
        elif clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "(":
           c_t += " "
    clear_text = c_t #1 whitespace added among numbers and text
    return clear_text

def check(page): #takes lines of text
    report = ["Консолидированный отчет о финансовом положении", "БУХГАЛТЕРСКИЙ БАЛАНС", "Консолидированный отчет о финансовом положении",
              "Консолидированный отчет о совокупном доходе", "ОТЧЕТ О ФИНАНСОВЫХ РЕЗУЛЬТАТАХ", "Консолидированный отчет о прибылях и убытках и прочем совокупном доходе",
              "Консолидированный отчет о движении денежных средств", "ОТЧЕТ ОБ ИЗМЕНЕНИЯХ КАПИТАЛА", "Консолидированный отчет об изменениях в капитале",
              "Консолидированный отчет об изменениях в капитале", "ОТЧЕТ О ДВИЖЕНИИ ДЕНЕЖНЫХ СРЕДСТВ", "Консолидированный отчет о движении денежных средств",
              ]
    oglavlenie = ["Содержание", "СОДЕРЖАНИЕ"]
    for stroka in page.splitlines():
        for line in oglavlenie:
            if " ".join(stroka.split()).count(line) >= 1:
                return []
        for headline in report:
            if " ".join(stroka.split()).count(headline) >= 1:
                return page
    return []

def read_content(filename): #takes file and returns list of string lists
    print("Reading content")
    _pdf = open(filename, 'rb')
    pdf_file = PyPDF2.PdfFileReader(_pdf, strict=False)
    page_dohod = pdf_file.pages
    for page in page_dohod:
        info = page.extract_text()
        info = edit_data(text = info) #info now is list
        if len(info) != 0 and len(pages) < 4:
            pages.append(info)
    print("Content ready")
    return pages
        
def collect_data(pages, measuring_unit):
    viruchka_list = ["Выручка"]
    pribyl_list = ["Прибыль за год", "Чистая прибыль отчетного периода"]
    for line in pages[1]:
        for name in viruchka_list:
            if line.count(name) >= 1 and is_valid(line) == True:
                viruchka_parts = line.split("  ")[1].split()
                ticker.viruchka = int("".join(viruchka_parts[1:len(viruchka_parts)])) * measuring_unit
                print(f"Выручка - {ticker.viruchka}")
        for name in pribyl_list:
            if line.count(name) >= 1 and is_valid(line) == True:
                ticker.pribyl = int("".join(line.split("  ")[1].split())) * measuring_unit
                print(f"Прибыль - {ticker.pribyl}")

def is_valid(line):
    for i in line.strip():
        if i.isdigit() == True:
            return True
    return False

def print_data(pages):
    for page in pages:
        for line in page:
            print(line)
            print("____________________________")

def get_price(ticker):
    pass

def analyze_data():
    pass



#def tab(url):
#    data = tabula.read_pdf(url, pages = '12', stream = True, guess=False)
#    print(data)
#def plumb(url):
#    pdf = pdfplumber.open(url)
#    table_setting={
#    "vertical_strategy": "text",
#    "horizontal_strategy": "text",
#    }
#    print(pdf.pages[12].extract_table(table_setting)) 
#plumb(url = filename)
#tab(url = filename)
#сторонние библиотеки для обработки pdf и таблиц


docs = ["https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf",
        "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf",
        "https://acdn.tinkoff.ru/static/documents/223e5d7f-6d12-429f-aae1-a25b154ea3e2.pdf",
        ]

file_url = docs[1]
ticker = Ticker()
filename = str()
pages = list()
measure_unit = int()

#start_time = time.time() #checking how long code executes

filename = get_file(tkr = ticker, url = file_url)
pages = read_content(filename)
collect_data(pages, measure_unit)
get_price(ticker)
#analyze_data(ticker)

#print(f"--- {time.time() - start_time} seconds ---")

