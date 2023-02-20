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
import camelot
import pandas as pd
#import matplotlib
#import tkinter
#from IPython.display import display
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
            return f"Количество акций - {ticker.amount} шт."
        if self.i == 3:
            return f"Прибыль составила - {ticker.pribyl} руб."
        if self.i == 4:
            return f"Выручка составила - {ticker.viruchka} руб."
        if self.i == 5:
            return f"p/e - {ticker.pe}"
        if self.i == 6:
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

def read_content(filename): #takes file and returns dict with all lines on info pages
    #print("Reading content")
    content_pages = list()
    number_pages = list()
    counter = 1
    with open(filename, 'rb') as f:
        pdf_file = PyPDF2.PdfFileReader(f, strict=False)
        page_dohod = pdf_file.pages
        for page in page_dohod:
            info = page.extract_text() #just strings
            if read_data(info, counter, filename) == True: #check if page contains needed tables
                number_pages.append(str(counter))
            counter += 1
    #print("Content ready")
    number_pages = ", ".join(number_pages)
    content_pages = camel(filename, number_pages, ['50,750,550,40']) #now dict with page info
    for i in content_pages.items():
        print(i)
    return content_pages

def read_data(text, counter, filename): #takes whole str page and return True/False if page contains needed tables and read amount of stocks and measure units of pages
    if ticker.amount == 0:
           find_amount(text, counter, filename)
    if check(text) == False: #checks if the page is in the list
        return False
    know_measure(text)
    return True

def camel(filename, pages, table_areas, st = ""): #takes file and number of pages and returns 
    pages_list_raw = list()
    pages_dicts = dict()
    pdf_file = camelot.read_pdf(filename, flavor = "stream", pages = pages, table_areas = table_areas, strip_text = st)
    for i in pdf_file:
        #camelot.plot(i, kind = 'contour').show()
        #matplotlib.pyplot.show(block=True)
        result = i.df
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 2000)
        pd.set_option('display.width', 500)
        result_dict = result.to_dict(orient = "index")
        for i in result_dict.items(): 
            pages_list_raw.append(i)
    #for i in pages_list_raw:
    #    print(i)
    pages_dicts = take_info(pages_list_raw)
    return pages_dicts

#TODO algo to now what actual number to get
def take_info(pages_raw): #takes list with dicts and returns dict (info: latest number)
    pages_dict = dict()
    for line in pages_raw:  #line look like: [(line_number, dict)]
        items_raw = list()
        dictt = line[1]
        for i in dictt.values(): #read non-empty values and ignore notes
            if i != "" and len(i) > 2:
                items_raw.append(i) 
        if len(items_raw) > 1:
            pages_dict.setdefault(items_raw[0], items_raw[1]) #todo [1:len(items_raw)] to get whole data
        elif len(items_raw) == 1:
            pages_dict.setdefault(items_raw[0], "")
        """ In case I want to combine lines
        #if len(items_raw) > 1 and mark == False:
        #    pages_dict.setdefault(items_raw[0], items_raw[1:len(items_raw)])
        #    continue
        #if len(items_raw) == 1:
        #    pages_dict.setdefault(items_raw[0], "")
        #    mark = True
        #    continue
        #if len(items_raw) > 1 and mark == True:
        #    key = pages_dict.popitem()
        #    pages_dict.setdefault(key[0]+items_raw[0], items_raw[1:len(items_raw)])
        #    mark = False
        #    continue
        """
    return pages_dict

def check(page): #takes lines of text and check if page is needed
    report = ["Консолидированный отчет о финансовом положении", "БУХГАЛТЕРСКИЙ БАЛАНС", "Консолидированный отчет о финансовом положении",
              "Консолидированный отчет о совокупном доходе", "ОТЧЕТ О ФИНАНСОВЫХ РЕЗУЛЬТАТАХ", "Консолидированный отчет о прибылях и убытках и прочем совокупном доходе",
              "Консолидированный отчет о движении денежных средств", "ОТЧЕТ ОБ ИЗМЕНЕНИЯХ КАПИТАЛА", "Консолидированный отчет об изменениях в капитале",
              "Консолидированный отчет об изменениях в капитале", "ОТЧЕТ О ДВИЖЕНИИ ДЕНЕЖНЫХ СРЕДСТВ", "Консолидированный отчет о движении денежных средств",
              "Консолидированный отчет о прибыли или убытке", "Консолидированный отчет о финансовом положении",
              "Консолидированный Отчет о финансовом положении", "Консолидированный Отчет о прибылях и убытках", "Консолидированный Отчет о совокупном доходе", 
              "Консолидированный Отчет о движении денежных средств"
              ]
    oglavlenie = ["Содержание", "СОДЕРЖАНИЕ"]
    #print(page)
    for stroka in page.splitlines():
        for line in oglavlenie:
            if " ".join(stroka.split()).count(line) >= 1:
                return False
        for headline in report:
            if " ".join(stroka.split()).count(headline) >= 1:
                #print(stroka)
                return True
    return False

def collect_data(pages, measuring_unit): #takes dict and finds needed params
    #print("Find necessary data")
    viruchka_list = ["Выручка"]
    pribyl_list = ["Прибыль за год", "Чистая прибыль отчетного периода", "Прибыль за отчетный год"]
    for name in viruchka_list:
        if pages.get(name) != None:
            viruchka_line = pages.get(name)
            viruchka = "".join(viruchka_line.split())
            #print(measuring_unit)
            ticker.viruchka = int(viruchka) * measuring_unit
            print(f"Выручка - {ticker.viruchka}")
    for name in pribyl_list:
        if pages.get(name) != None:
            pribyl_line = pages.get(name)
            pribyl = "".join(pribyl_line.split())
            #print(measuring_unit)
            ticker.pribyl = int(pribyl) * measuring_unit
            print(f"Прибыль - {ticker.pribyl}")

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

def know_notes(line): #checks if there notes
    notes_list = ["Примечание", "Поясн", "Прим"]
    for word in notes_list:
        if line.find(word) != 0:
            return True

def know_measure(text):
    global measure_unit
    for line in text.splitlines():
        #print(line)
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

def find_amount(text, counter, filename): #takes text and find amount of shares 
    amount_key = str()
    amount_value = int()
    measure_unit_thousands_list = ["в тысячах", "тысяч"]
    measure_unit_mil_list = ["в млн", "млн"]
    shares_amount_list = ["Средневзвешенное количество выпущенных обыкновенных акций", "Средневзвешенное количество обыкновенных акций",
                          "Средневзвешенное количество акций"]
    for line in text.splitlines():
        line = line.strip()
        #print(line)
        if len(line) != 0:
            for name in shares_amount_list:
                if line.count(name) >= 1:
                    #print(line)
                    amount_dict = camel(filename, str(counter), ['90,800,550,40'], "\n") #dict with info on the page
                    items = list(amount_dict.items()) #making list to have indexes in case when info splitted into 2 lines
                    amount_key, amount_value = get_key_value(items, name) 
                    for mu in measure_unit_thousands_list:
                        if amount_key.count(mu) > 0:
                            ticker.amount = float(amount_value) * 1000       
                            #print(f"Количество акций - {ticker.amount} шт.")
                            return True
                    for mu in measure_unit_mil_list:
                        if amount_key.count(mu) > 0:
                            ticker.amount = float(amount_value) * 1000000
                            #print(f"Количество акций - {ticker.amount} шт.")
                            return True
                    ticker.amount = float(amount_value)
                    #print(f"Количество акций - {ticker.amount} шт.")
                    return True

def get_key_value(items, name): #func in case line splitted into 2 lines, we get next line
    for key,value in items:
        #print(key, value)
        if key.count(name) > 0:
            amount_key = key
            amount_value = value
            #print(amount_key, amount_value)
            if amount_value == "": 
                index_actual_pair = items.index((key, value))
                amount_tuple = items[index_actual_pair + 1] #tuple (info, data) from next line
                amount_value = amount_tuple[1].split("  ")[0]
                amount_key = amount_tuple[0]
                amount_value = amount_tuple[1]
            amount_key, amount_value = correct_data(amount_key, amount_value) #check if key = info and values = numbers and all correct
            amount_value = "".join(amount_value.split())
            #print(amount_key, "|", amount_value)
            return (amount_key, amount_value)

def correct_data(key, value):
    i = int()
    if value == "":
        if is_here_alnum(key) == "alnum":
            while i < key.count(" "):
                whitespace = key.find(" ")
                if alldigit(key[whitespace:len(key)]) == True:
                    new_key = key[0:whitespace]
                    new_value = key[whitespace:len(key)].split(" ")
                    return (new_key, new_value[0])
                i += 1
    else:
        if is_here_alnum(key) == "alpha" and alldigit(value):
            new_value = value.split("  ")
            return (key, new_value[0])

"""
Not used, on some case
"""
def edit_whitespaces(clear_text): #clearing line of text, return ???
    print(clear_text)
    whitespace_list = list() 
    if len(clear_text) != 0:
        clear_text = clear_text.strip()
        amount_whitespaces = clear_text.count(" ")
        start = 0
        x = 0
        while x != amount_whitespaces:
            whitespace = clear_text.find(" ", start)
            start = whitespace + 1
            x += 1
            if alldigit(clear_text[whitespace:len(clear_text)]) == True:
                if clear_text[whitespace + 1] == " " and clear_text[whitespace + 2].isdigit() == True:
                    continue
                if clear_text[whitespace + 1] == " ":
                    whitespace_list.append(whitespace)
                    continue
        clear_text = replace_whitespace(clear_text, whitespace_list)
        print(clear_text)
        parts = clear_text.rsplit("  ", maxsplit = 2)
        if len(parts) == 3:
            part1_parts = parts[0].rsplit(" ", 1)
            if part1_parts[1].isdigit():
                part1 = part1_parts[0] #text part of line
            else:
                part1 = parts[0]
            part2 = parts[1]
            part3 = parts[2]
            return (part1, part2, part3) 
        else: 
            return (parts[0],"","")
    else:
        return ("","","")

"""
Not used, on some case
"""
def replace_whitespace(line, index_list): #remove one whitespace from double whitespaces
    patch = list(line)
    counter = 0
    for i in index_list:
        patch.pop(i - counter)
        counter += 1
    return "".join(patch)

def alldigit(line):
    edited_line = "".join(line.split())
    edited_line = edited_line.replace("(","")
    edited_line = edited_line.replace(")","")
    if edited_line.isdigit() == True:
        return True
    return False

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
    pages = read_content(str(filename))
    collect_data(pages, measure_unit)
    get_price(method)
    analyze_data()
    #write_db()
    print_data()
    return (ticker.pe, ticker.ps)

ticker = Ticker()
filename = str()
pages = list()
measure_unit = int()
method = "t"

if __name__ == "__main__":
    name = "mtss"#input("Type ticker name: ")
    run(docs[1], name, method)
    

