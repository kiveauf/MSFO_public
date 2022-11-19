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
        self.url = str()
        self.name = str()
        self.pribyl = 0
        self.viruchka = 0
        self.price = float()
        self.amount = 0
        self.capitalization = float()
        self.pe = float()
        self.ps = float()

def get_file(tkr, name): # take url of the file
    file = requests.get(tkr.url)
    tkr.name = name.lower()
    filename = f"{tkr.name}_MSFO.pdf"
    with open(file = filename, mode = 'wb') as f:
        f.write(file.content)
    #print("Done")
    return filename

def read_content(filename): #takes file and returns list of string lists
    #print("Reading content")
    _pdf = open(filename, 'rb')
    pdf_file = PyPDF2.PdfFileReader(_pdf, strict=False)
    page_dohod = pdf_file.pages
    for page in page_dohod:
        info = page.extract_text()
        info = edit_data(text = info) #info now is list
        if len(info) != 0 and len(pages) < 4:
            pages.append(info)
    #print("Content ready")
    if len(pages) != 4:
        print("Есть ошибки прочтения")
        print(f"Количество страниц - {len(pages)}")
        return[]
    return pages

def edit_data(text): #takes whole str page and return list of str
    clear_text = str()
    stroki = list()
    if ticker.amount == 0:
           find_amount(text)
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
        know_measure(stroka)
    return stroki

def check(page): #takes lines of text
    report = ["Консолидированный отчет о финансовом положении", "БУХГАЛТЕРСКИЙ БАЛАНС", "Консолидированный отчет о финансовом положении",
              "Консолидированный отчет о совокупном доходе", "ОТЧЕТ О ФИНАНСОВЫХ РЕЗУЛЬТАТАХ", "Консолидированный отчет о прибылях и убытках и прочем совокупном доходе",
              "Консолидированный отчет о движении денежных средств", "ОТЧЕТ ОБ ИЗМЕНЕНИЯХ КАПИТАЛА", "Консолидированный отчет об изменениях в капитале",
              "Консолидированный отчет об изменениях в капитале", "ОТЧЕТ О ДВИЖЕНИИ ДЕНЕЖНЫХ СРЕДСТВ", "Консолидированный отчет о движении денежных средств",
              "Консолидированный отчет о прибыли или убытке", "Консолидированный отчет о финансовом положении",
              "Консолидированный Отчет о финансовом положении", "Консолидированный Отчет о прибылях и убытках", "Консолидированный Отчет о совокупном доходе", 
              "Консолидированный Отчет о движении денежных средств"
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

def edit_whitespaces(clear_text): #clearing line of text
    clear_text = clear_text.replace("   ", "  ")
    if len(clear_text) != 0:
        c_t = str()
        x = 0
        start = 0
        amount_ws = clear_text.count("  ") + 1
        while x != amount_ws:
            x += 1
            whitespaces = clear_text.find("  ", start)
            start = whitespaces
            if (whitespaces - 1 >= 0) and (whitespaces + 2 < len(clear_text)):
                if clear_text[whitespaces - 1].isdigit() == False and clear_text[whitespaces + 2].isdigit() == False:
                    clear_text = replace_whitespace(clear_text, whitespaces)
                    continue
            elif (whitespaces == 0) and (whitespaces + 2 < len(clear_text)):
                if clear_text[whitespaces + 2].isdigit() == False:
                    clear_text = replace_whitespace(clear_text, whitespaces)
                    continue
            elif (whitespaces - 1 >= 0) and (whitespaces + 2 == len(clear_text) - 1):
                if clear_text[whitespaces - 1].isdigit() == False:
                    clear_text = replace_whitespace(clear_text, whitespaces)
                    continue
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
            elif clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1].isdigit() == True and is_here_alnum(clear_text[i:len(clear_text)]) == "digit":
               c_t += " "
            elif clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "(":
               c_t += " "
            elif clear_text[i] == " " and clear_text[i-1] == "." and clear_text[i+1].isdigit() == True:
               c_t += " "
            elif clear_text[i] == " " and clear_text[i-1] == ")" and is_here_alnum(clear_text[i:len(clear_text)]) == "digit" and clear_text[i+1] != " ":
               c_t += " "
        clear_text = c_t.strip() + clear_text[len(clear_text) - 1] #1 whitespace added among numbers and text
        return clear_text
    else:
        return ""

def collect_data(pages, measuring_unit): #reads the page and finds needed params
    #print("Find necessary data")
    viruchka_list = ["Выручка"]
    pribyl_list = ["Прибыль за год", "Чистая прибыль отчетного периода", "Прибыль за отчетный год"]
    for line in pages[1]:
        #notes = know_notes(line)
        for name in viruchka_list:
            if line.count(name) >= 1 and is_here_num(line) == True:
                #print(line)
                viruchka_line = edit_line(line).split("  ")[0]
                viruchka = "".join(viruchka_line.split())
                ticker.viruchka = int(viruchka) * measuring_unit
                #print(f"Выручка - {ticker.viruchka}")
        for name in pribyl_list:
            if line.count(name) >= 1 and is_here_num(line) == True:
                #print(line)
                ticker.pribyl = int("".join(line.split("  ")[1].split())) * measuring_unit
                #print(f"Прибыль - {ticker.pribyl}")

def is_here_num(line): #if line contains number
    for i in line.strip():
        if i.isdigit() == True:
            return True
    return False

def is_here_alnum(line): #tells what line contains
    counter = [False, False]
    for i in line.strip():
        if i.isdigit() == True:
            counter[0] = True
        if i.isalpha() == True:
            counter[1] = True
    #print(counter[0], counter[1])
    if counter[0] == True and counter[1] == True:
        return "alnum"
    if counter[0] == True and counter[1] == False:
        return "digit"
    if counter[0] == False and counter[1] == True:
        return "alpha"
    return "other"

def edit_line(line): # do some editing with line containing viruchku
    viruchka_parts = line.partition("  ")[2].strip()
    space = viruchka_parts.find(" ")
    viruchka_parts = viruchka_parts[space:len(viruchka_parts)].strip()
    return viruchka_parts

def replace_whitespace(line, index): #remove one whitespace from double whitespaces
    newline = str()
    for i in range(len(line)-1):
        if i == index:
            continue
        newline += line[i]
    return newline

def know_notes(line): #checks if there notes
    notes_list = ["Примечание", "Поясн", "Прим"]
    for word in notes_list:
        if line.find(word) != 0:
            return True

def know_measure(line):
    global measure_unit
    for word in line.split():
            if word in ["тыс.", "тыс", "тысячах", "thousands"]:
                measure_unit = 1000 #measuring unit
            if word in ["млн.", "млн", "миллионах", "millions", "Млн"]:
                measure_unit = 1000000 #measuring unit
        
def print_pages(pages):
    for page in pages:
        for line in page:
            print(line)
            print("____________________________")

def print_data():
    print(f"Прибыль составила - {ticker.pribyl} руб.")
    print(f"Выручка составила - {ticker.viruchka} руб.")
    print(f"p/e - {ticker.pe}")
    print(f"p/s - {ticker.ps}")

def get_price():
    parser()
    #tinkoff_api()

def parser(): #using selenium to get all info because of javascript
    #print("Getting price and amount of shares")
    site_url = f"https://bcs-express.ru/kotirovki-i-grafiki/{ticker.name}"
    service = Service(executable_path='C:\Program Files\ChromeDriver\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    page = webdriver.Chrome(service=service, options= options)
    page.implicitly_wait(2) # just to wait until page will load 
    page.get(site_url)
    price_sel = page.find_element(By.CLASS_NAME, 'gvxn._cou.o37l').text
    ticker.price = float(price_sel.replace(" ", "").replace(",", "."))
    page.quit()
    #amount_sel = page.find_elements(By.CLASS_NAME, 'Yai9')
    #ticker.amount = float(amount_sel[5].text.replace(" ", "").replace(",", "."))

def find_amount(text): #find amount of shares
    global amount_line
    measure_unit_thousands_list = ["в тысячах", "тысяч"]
    measure_unit_mil_list = ["в млн", "млн"]
    shares_amount_list = ["Средневзвешенное количество выпущенных обыкновенных акций", "Средневзвешенное количество обыкновенных акций",
                          "Средневзвешенное количество акций", "Средневзвешенное количество акций"]
    for line in text.splitlines():
        line = line.strip()
        #print(line)
        if len(line) != 0:
            if line[0].isupper() == True:
                amount_line = line
            if is_here_num(line) == False and line[0].isupper() == False:
                amount_line += " " + line
            if is_here_num(line) == True and line[0].isupper() == False:
                amount_line += " " + line
            if is_here_num(line) == True and amount_line[0].isupper() == True:
                for name in shares_amount_list:
                    if amount_line.count(name) >= 1:
                        amount_line = edit_whitespaces(amount_line)
                        #print(amount_line)
                        for mu in measure_unit_thousands_list:
                            if amount_line.count(mu) >= 1:
                                ticker.amount = float(amount_line.strip().split("  ")[1].replace(" ", "").replace(",", "")) * 1000
                                #print(f"Количество акций - {ticker.amount} шт.")
                                return True
                        for mu in measure_unit_mil_list:
                            if amount_line.count(mu) >= 1:
                                ticker.amount = float(amount_line.strip().split("  ")[1].replace(" ", "").replace(",", "")) * 1000000
                                #print(f"Количество акций - {ticker.amount} шт.")
                                return True
                        ticker.amount = float(amount_line.strip().split("  ")[1].replace(" ", "").replace(",", ""))
                        #print(f"Количество акций - {ticker.amount} шт.")
                        return True

def tinkoff_api():
    pass

def analyze_data(): #just do the math
    ticker.capitalization = ticker.price * ticker.amount
    if ticker.pribyl != 0:
        ticker.pe = ticker.capitalization / ticker.pribyl
    if ticker.viruchka != 0:
        ticker.ps = ticker.capitalization / ticker.viruchka

def timetrack(func):
    def count_time(*arg):
        start_time = time.time() #checking how long code executes
        result = func(*arg)
        print(f"--- {time.time() - start_time} seconds ---")
        return result
    return count_time

@timetrack
def run(url, name):#just run the program
    ticker.url = url
    filename = get_file(tkr = ticker, name = name)
    pages = read_content(filename)
    collect_data(pages, measure_unit)
    get_price()
    analyze_data()
    print_data()
    return (len(pages), ticker.pe, ticker.ps)


docs = [
        "https://www.magnit.com/upload/iblock/4e4/%D0%905.12_%D0%9F%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%BD%D0%B0%D1%8F%20%D1%84%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%BE%D0%B2%D0%B0%D1%8F%20%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C%20%D1%81%20%D0%90%D0%97_%D0%9C%D0%B0%D0%B3%D0%BD%D0%B8%D1%82_2021%20(%D1%80%D1%83%D1%81%D1%81).pdf",
        "https://mts.ru/upload/contents/10677/mts_ras_fs_21-r.pdf",
        "https://acdn.tinkoff.ru/static/documents/223e5d7f-6d12-429f-aae1-a25b154ea3e2.pdf",
        "https://lukoil.ru/FileSystem/9/577502.pdf",
        "http://www.rushydro.ru/upload/iblock/89e/IFRS-RusHydro_2112_rrus.pdf"
        ]

ticker = Ticker()
filename = str()
pages = list()
measure_unit = int()
amount_line = str()

if __name__ == "__main__":
    name = input("Type ticker name: ")
    run(docs[1], name)
    

