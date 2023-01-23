"""
script to collect and analyze data from msfo sheets and real stock price
use python 3.9
"""

import PyPDF2
import requests
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
from tinkoff.invest import Client
import mysql.connector as sql
from dotenv import load_dotenv
from DocsTest import docs
#import asyncio
#import aiohttp
#import getpass
                                             
load_dotenv() #using this to get enviroment custom-made constant
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
        self.i = 0

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        self.i += 1
        if self.i == 1:
            return f"Цена составила - {ticker.price} руб."
        if self.i == 2:
            return f"Прибыль составила - {ticker.pribyl} руб."
        if self.i == 3:
            return f"Выручка составила - {ticker.viruchka} руб."
        if self.i == 4:
            return f"p/e - {ticker.pe}"
        if self.i == 5:
            return f"p/s - {ticker.ps}"
        raise StopIteration()

def get_file(tkr, name): # take url of the file
    file = requests.get(tkr.url)
    tkr.name = name.lower()
    filename = f"{tkr.name}_MSFO.pdf"
    with open(file = filename, mode = 'wb') as f:
        f.write(file.content)
    #print("Done")
    return filename

def read_content(filename): #takes file and returns dict (info : (data x-year, data y-year))
    #print("Reading content")
    content_pages = dict()
    with open(filename, 'rb') as f:
        pdf_file = PyPDF2.PdfFileReader(f, strict=False)
        page_dohod = pdf_file.pages
        for page in page_dohod:
            info = page.extract_text() #just strings
            info = edit_data(text = info) #info now is tuple (info, data x-year, data y-year)
            if len(info) != 0 and len(content_pages) < 4:
                content_pages.setdefault(info[0],(info[1], info[2]))
    #print("Content ready")
    if len(content_pages) != 4:
        print("Есть ошибки прочтения")
        print(f"Количество страниц - {len(pages)}")
        return[]
    return content_pages

def edit_data(text): #takes whole str page and return list of str
    clear_text = str()
    stroki = dict()
    if ticker.amount == 0:
           find_amount(text)
    if check(text) == False: #checks if the page is in the list
        return []
    for stroka in text.splitlines():
        if len(stroka.strip()) == 0 or stroka == "\n":
            stroka = stroka.strip(" \n")
            continue
        if stroka[0].isupper() == True:
            clear_text = edit_whitespaces(clear_text)
            stroki = clear_text
            #print(stroki)
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
                return False
        for headline in report:
            if " ".join(stroka.split()).count(headline) >= 1:
                return True
    return False

def edit_whitespaces(clear_text): #clearing line of text
    print(clear_text)
    whitespace_list = list()
    c_t = str()  #TODO
    if len(clear_text) != 0:
        clear_text = clear_text.strip()
        amount_whitespaces = clear_text.count(" ")
        start = 0
        x = 0
        while x != amount_whitespaces:
            whitespace = clear_text.find(" ", start)
            #print(whitespace)
            start = whitespace + 1
            x += 1
            if clear_text[whitespace - 1].isdigit() == False and clear_text[whitespace + 1] == " " and clear_text[whitespace + 2].isdigit() == False:
                whitespace_list.append(whitespace)
                continue
            #if clear_text[whitespace - 1].isdigit() == True and clear_text[whitespace + 1] == " " and clear_text[whitespace + 2].isdigit() == False:
            #    whitespace_list.append(whitespace)
            #    continue
            #if clear_text[whitespace - 1].isdigit() == True and clear_text[whitespace + 1] == " " and clear_text[whitespace + 2].isdigit() == True:
            #    whitespace_list.append(whitespace)
            #    continue
        clear_text = replace_whitespace(clear_text, whitespace_list)
        #for i in range(len(clear_text) - 1):
        #    if clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1] == ",":
        #       continue
        #    if clear_text[i] == " " and clear_text[i+1] == "/" and clear_text[i-1].isalpha() == True:
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == "/" and clear_text[i+1].isalpha() == True:
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "/":
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == "/" and clear_text[i+1] == "(":
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == "(" and clear_text[i+1].isalpha() == True:
        #       continue
        #    if clear_text[i] == " " and clear_text[i+1] == ")" and clear_text[i-1].isalpha() == True:
        #       continue
        #    c_t += clear_text[i]
        #    if clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1] == "(" and clear_text[i+2].isdigit() == True:
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1].isdigit() == True and is_here_alnum(clear_text[i:len(clear_text)]) == "digit":
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "(":
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1] == "." and clear_text[i+1].isdigit() == True:
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1] == ")" and is_here_alnum(clear_text[i:len(clear_text)]) == "digit" and clear_text[i+1] != " ":
        #       c_t += " "
        #clear_text = c_t.strip() + clear_text[len(clear_text) - 1] #1 whitespace added among numbers and text
        #while x != amount_ws:
        #    x += 1
        #    whitespaces = clear_text.find("  ", start)
        #    start = whitespaces #index of the first whitespace
        #    if (whitespaces - 1 >= 0) and (whitespaces + 2 < len(clear_text)): #if whitespace isn't first and third from the end
        #        if clear_text[whitespaces - 1].isdigit() == False and clear_text[whitespaces + 2].isdigit() == False:
        #            clear_text = replace_whitespace(clear_text, whitespaces)
        #            continue
        #    elif (whitespaces == 0) and (whitespaces + 2 < len(clear_text)): #if whitespace isn't first and third from the end
        #        if clear_text[whitespaces + 2].isdigit() == False:
        #            clear_text = replace_whitespace(clear_text, whitespaces)
        #            continue
        #    elif (whitespaces - 1 >= 0) and (whitespaces + 2 == len(clear_text) - 1): #if whitespace isn't first and third from the end
        #        if clear_text[whitespaces - 1].isdigit() == False:
        #            clear_text = replace_whitespace(clear_text, whitespaces)
        #            continue
        #for i in range(len(clear_text) - 1):
        #    if clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1] == ",":
        #       continue
        #    if clear_text[i] == " " and clear_text[i+1] == "/" and clear_text[i-1].isalpha() == True:
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == "/" and clear_text[i+1].isalpha() == True:
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "/":
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == "/" and clear_text[i+1] == "(":
        #       continue
        #    if clear_text[i] == " " and clear_text[i-1] == "(" and clear_text[i+1].isalpha() == True:
        #       continue
        #    if clear_text[i] == " " and clear_text[i+1] == ")" and clear_text[i-1].isalpha() == True:
        #       continue
        #    c_t += clear_text[i]
        #    if clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1] == "(" and clear_text[i+2].isdigit() == True:
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1].isalpha() == True and clear_text[i+1].isdigit() == True and is_here_alnum(clear_text[i:len(clear_text)]) == "digit":
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1] == ")" and clear_text[i+1] == "(":
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1] == "." and clear_text[i+1].isdigit() == True:
        #       c_t += " "
        #    elif clear_text[i] == " " and clear_text[i-1] == ")" and is_here_alnum(clear_text[i:len(clear_text)]) == "digit" and clear_text[i+1] != " ":
        #       c_t += " "
        #clear_text = c_t.strip() + clear_text[len(clear_text) - 1] #1 whitespace added among numbers and text
        parts = clear_text.rsplit("  ", maxsplit = 2)
        #print(parts)
        if len(parts) == 3:
            part1 = parts[0].rsplit(" ", 1)[0] #text part of line
            part2 = parts[1]
            part3 = parts[2]
            return (part1, part2, part3) 
        else: 
            return (parts[0],"","")
    else:
        return ""

def collect_data(pages, measuring_unit): #reads the page and finds needed params
    #print("Find necessary data")
    viruchka_list = ["Выручка"]
    pribyl_list = ["Прибыль за год", "Чистая прибыль отчетного периода", "Прибыль за отчетный год"]
    for name in viruchka_list:
        if pages.get(name, None) != None:    
            viruchka_line = pages[name][0]
            viruchka = "".join(viruchka_line.split())
            ticker.viruchka = int(viruchka) * measuring_unit
            #print(f"Выручка - {ticker.viruchka}")
    for name in pribyl_list:
        if pages.get(name, None) != None:  
            pribyl_line = pages[name][0]
            ticker.pribyl = int("".join(pribyl_line.split())) * measuring_unit
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

#def edit_line(line): # do some editing with line containing viruchku
#    viruchka_parts = line.partition("  ")[2].strip()
#    space = viruchka_parts.find(" ")
#    viruchka_parts = viruchka_parts[space:len(viruchka_parts)].strip()
#    return viruchka_parts

def replace_whitespace(line, index_list): #remove one whitespace from double whitespaces
    patch = list(line)
    counter = 0
    for i in index_list:
        patch.pop(i - counter)
        counter += 1
    return "".join(patch)

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
    for i in ticker:
        print(i)

def get_price(method):
    if method == "p":
        parser()
    if method == "t":
        tinkoff_api()

def parser(): #using selenium to get all info because of javascript
    #print("Getting price and amount of shares")
    site_url = f"https://bcs-express.ru/kotirovki-i-grafiki/{ticker.name}"
    service = Service(executable_path='C:\Program Files\ChromeDriver\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    page = webdriver.Chrome(service=service, options= options)
    page.implicitly_wait(2) # just to wait until page will load 
    page.get(site_url)
    price_sel = page.find_element(By.CLASS_NAME, 'Here.EWHp.Dlhk').text
    ticker.price = float(price_sel.replace(" ", "").replace(",", "."))
    page.quit()
    #amount_sel = page.find_elements(By.CLASS_NAME, 'Yai9')
    #ticker.amount = float(amount_sel[5].text.replace(" ", "").replace(",", "."))

def find_amount(text): #find amount of shares  #TODOOOOO
    amount_line = str()
    measure_unit_thousands_list = ["в тысячах", "тысяч"]
    measure_unit_mil_list = ["в млн", "млн"]
    shares_amount_list = ["Средневзвешенное количество выпущенных обыкновенных акций", "Средневзвешенное количество обыкновенных акций",
                          "Средневзвешенное количество акций"]
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
    ticker_data = str()
    ticker_price_quotation = str()
    ticker_price_response = str()
    token = os.environ["TOKEN"]
    with Client(token) as client:
        ticker_data = client.instruments.find_instrument(query = ticker.name).instruments
        #print(ticker_data)
        for i in ticker_data:
            if i.ticker.lower() == ticker.name:
                ticker_data_choice = i
        ticker_price_response = client.market_data.get_last_prices(figi = [ticker_data_choice.figi])
        ticker_price_quotation = ticker_price_response.last_prices[0].price
        ticker.price = float(str(ticker_price_quotation.units) + "." + str(ticker_price_quotation.nano))
        #print(ticker_price)

def write_db():
    if ticker.pe != 0 and ticker.ps != 0:
        try:
            with sql.connect(host="127.0.0.1", user = "Kirill", #input("Type user name: "), 
                             password = "password", #getpass.getpass("Type password: "), 
                             database = "fm") as connection:
                query_select =  "SELECT * from fm_table"
                query_insert = "INSERT INTO fm_table (ticker, revenue, income, pe, ps, amount, price, cap) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                with connection.cursor() as cursor:
                    #to see columns
                    cursor.execute("desc fm_table")
                    print_db([column[0] for column in cursor.fetchall()])   
                    #to add data
                    data = (ticker.name, ticker.viruchka, ticker.pribyl, ticker.pe,
                           ticker.ps, ticker.amount, ticker.price, ticker.capitalization)
                    cursor.execute(query_insert, data)
                    connection.commit()
                    #to print all lines
                    cursor.execute(query_select)
                    result = cursor.fetchall()
                    for line in result:
                        print_db(line)
        except sql.Error as e:
            print(e)

def print_db(line):
    for i in line:
        print(f'{i:<18}',end = "")
    print(end="\n")

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
def run(url, name, method):#just run the program
    ticker.url = url
    filename = get_file(tkr = ticker, name = name)
    pages = read_content(filename)
    collect_data(pages, measure_unit)
    get_price(method)
    analyze_data()
    #write_db()
    print_data()
    return (len(pages), ticker.pe, ticker.ps)

ticker = Ticker()
filename = str()
pages = list()
measure_unit = int()
method = "t"

if __name__ == "__main__":
    name = "hydr"#input("Type ticker name: ")
    run(docs[4], name, method)
    

