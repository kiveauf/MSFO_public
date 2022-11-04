#script to collect and analyze data from msfo sheets and real stock price

import PyPDF2
import requests
import logging
import time
import bs4
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.CRITICAL)

class Ticker():
    def __init__(self):
        self.name = str()
        self.pribyl = 0
        self.viruchka = 0
        self.price = float()
        self.amount = 0
        self.capitalization = float()
        self.pe = float()
        self.ps = float()

def get_file(tkr, url): # take url of the file
    file = requests.get(url)
    tkr.name = input("Type ticker: ")
    tkr.name = tkr.name.lower()
    filename = f"{tkr.name}_MSFO.pdf"
    open(file = filename, mode = 'wb').write(file.content)
    print("Done")
    return filename

def edit_data(text): #takes whole str page and return list of str
    global measure_unit
    clear_text = str()
    stroki = list()
    if len(check(text)) == 0: #checks if the page is in the list
        return []
    for stroka in text.splitlines():
        if len(stroka.strip()) == 0 or stroka == "\n":
            stroka = stroka.strip(" \n")
            continue
        if stroka[0].isupper() == True:
            clear_text = edit_whitespaces(clear_text)
            stroki.append(clear_text)
            clear_text = ""
        clear_text += stroka + " " #adding words to one line
        for word in stroka.split():
            if word in ["тыс.", "тыс", "тысячах", "thousands"]:
                measure_unit = 1000 #measuring unit
            if word in ["млн.", "млн", "миллионах", "millions", "Млн"]:
                measure_unit = 1000000 #measuring unit
    return stroki

def edit_whitespaces(clear_text): # clearing line of text
    if len(clear_text) != 0:
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
            elif clear_text[i] == " " and clear_text[i-1] == "." and clear_text[i+1].isdigit() == True:
               c_t += " "
        clear_text = c_t.strip() + clear_text[len(clear_text) - 1] #1 whitespace added among numbers and text
        return clear_text
    else:
        return ""

def check(page): #takes lines of text
    report = ["Консолидированный отчет о финансовом положении", "БУХГАЛТЕРСКИЙ БАЛАНС", "Консолидированный отчет о финансовом положении",
              "Консолидированный отчет о совокупном доходе", "ОТЧЕТ О ФИНАНСОВЫХ РЕЗУЛЬТАТАХ", "Консолидированный отчет о прибылях и убытках и прочем совокупном доходе",
              "Консолидированный отчет о движении денежных средств", "ОТЧЕТ ОБ ИЗМЕНЕНИЯХ КАПИТАЛА", "Консолидированный отчет об изменениях в капитале",
              "Консолидированный отчет об изменениях в капитале", "ОТЧЕТ О ДВИЖЕНИИ ДЕНЕЖНЫХ СРЕДСТВ", "Консолидированный отчет о движении денежных средств",
              "Консолидированный отчет о прибыли или убытке", "Консолидированный отчет о финансовом положении",
              ]
    oglavlenie = ["Содержание", "СОДЕРЖАНИЕ"]
    for stroka in page.splitlines():
        for line in oglavlenie:
            if " ".join(stroka.split()).count(line) >= 1:
                return []
        for headline in report:
            if " ".join(stroka.split()).count(headline) >= 1:
                return page
        if ticker.amount == 0:
           find_amount(stroka)
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
    if len(pages) != 4:
        print("Есть ошибки прочтения")
        print(f"Количество страниц - {len(pages)}")
        return[]
    return pages
        
def collect_data(pages, measuring_unit):
    print("Find necessary data")
    viruchka_list = ["Выручка"]
    pribyl_list = ["Прибыль за год", "Чистая прибыль отчетного периода", "Прибыль за отчетный год"]
    for line in pages[1]:
        print(line)
        for name in viruchka_list:
            if line.count(name) >= 1 and is_valid(line) == True:
                viruchka_parts = line.split("  ")[1].split()
                ticker.viruchka = int("".join(viruchka_parts[1:len(viruchka_parts)])) * measuring_unit
                #print(f"Выручка - {ticker.viruchka}")
                print(line)
        for name in pribyl_list:
            if line.count(name) >= 1 and is_valid(line) == True:
                ticker.pribyl = int("".join(line.split("  ")[1].split())) * measuring_unit
                print(line)
                #print(f"Прибыль - {ticker.pribyl}")

def is_valid(line):
    for i in line.strip():
        if i.isdigit() == True:
            return True
    return False

def print_pages(pages):
    for page in pages:
        for line in page:
            print(line)
            print("____________________________")

def print_data():
    print(f"Прибыль составила - {ticker.pribyl}")
    print(f"Выручка составила - {ticker.viruchka}")
    print(f"p/e - {ticker.pe}")
    print(f"p/s - {ticker.ps}")

def get_price():
    parser()
    #tinkoff_api()

def parser(): #using selenium to get all info because of javascript
    print("Getting price and amount of shares")
    site_url = f"https://bcs-express.ru/kotirovki-i-grafiki/{ticker.name}"
    service = Service(executable_path='C:\Program Files\ChromeDriver\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    page = webdriver.Chrome(service=service, options= options)
    page.implicitly_wait(2) # just to wait until page will load 
    page.get(site_url)
    price_sel = page.find_element(By.CLASS_NAME, 'gvxn._cou.o37l').text
    ticker.price = float(price_sel.replace(" ", "").replace(",", "."))
    #amount_sel = page.find_elements(By.CLASS_NAME, 'Yai9')
    #ticker.amount = float(amount_sel[5].text.replace(" ", "").replace(",", "."))

def find_amount(line): #find amount of shares
    global amount_line
    measure_unit_list = ["в тысячах", "тысяч"]
    shares_amount_list = ["Средневзвешенное количество выпущенных обыкновенных акций", "Средневзвешенное количество обыкновенных акций",
                          "Средневзвешенное количество акций"]
    if line[0].isupper() == True:
        amount_line = line 
    if is_valid(line) == False and line[0].isupper() == False:
        amount_line += line
    if is_valid(line) == True and line[0].isupper() == False:
        amount_line += line
    if is_valid(line) == True:
        for name in shares_amount_list:
            if amount_line.count(name) >= 1:
                amount_line = edit_whitespaces(amount_line)
                for mu in measure_unit_list:
                    if amount_line.count(mu) >= 1:
                        print(amount_line)
                        ticker.amount = float(amount_line.strip().split("  ")[1].replace(" ", "").replace(",", "")) * 1000
                        print(ticker.amount)
                        return True
                print(amount_line)
                ticker.amount = float(amount_line.strip().split("  ")[1].replace(" ", "").replace(",", ""))
                print(ticker.amount)
                return True

def tinkoff_api():
    pass

def analyze_data():
    ticker.capitalization = ticker.price * ticker.amount
    if ticker.pribyl != 0:
        ticker.pe = ticker.capitalization / ticker.pribyl
    if ticker.viruchka != 0:
        ticker.ps = ticker.capitalization / ticker.viruchka

docs = ["https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf",
        "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf",
        "https://acdn.tinkoff.ru/static/documents/223e5d7f-6d12-429f-aae1-a25b154ea3e2.pdf",
        "https://cdn.phosagro.ru/upload/iblock/ebe/ebe1b9517163a4e5fc22821167c337ec.pdf",
        ]

file_url = docs[3]
ticker = Ticker()
filename = str()
pages = list()
measure_unit = int()
amount_line = str()

start_time = time.time() #checking how long code executes
filename = get_file(tkr = ticker, url = file_url)
pages = read_content(filename)
if len(pages) != 0:
    collect_data(pages, measure_unit)
    get_price()
    analyze_data()
    print_data()
print(f"--- {time.time() - start_time} seconds ---")

