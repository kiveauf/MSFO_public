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
import psycopg2 as psql
from dotenv import load_dotenv
from DocsTest import docs 
import camelot
import pandas as pd
import re
#import matplotlib
                                             
load_dotenv() #using this to get enviroment custom-made constant
logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.CRITICAL)

class Ticker():
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.pribyl = 0
        self.viruchka = 0
        self.price = float()
        self.amount = 0
        self.capitalization = float()
        self.measuring_unit = int()
        self.pe = float()
        self.ps = float()
        self.pages = list()
    
    def print_ticker_data(self):
        print("__print_ticker_data()___")
        for i in self.__dict__.items():
            print(i)
    
def get_file(url, name): # take url of the file
    file = requests.get(url)
    filename = f"{name.lower()}_MSFO.pdf"
    with open(file = filename, mode = 'wb') as f:
        f.write(file.content)
    return filename

def read_content(filename): #takes file and returns dict with all lines on info pages
    #print("Reading content")
    content_pages_raw = camel(filename, pages= '3-20', table_areas=['50,800,550,40']) #now dict with page info
    return content_pages_raw

def camel(filename, pages, table_areas, st = ""): #takes file and number of pages and returns 
    pages_list_raw = list()
    pdf_file = camelot.read_pdf(filename, flavor = "stream", pages = pages, table_areas = table_areas, strip_text = st, edge_tol=200)
    for page in pdf_file:
        #camelot.plot(i, kind = 'contour').show() # to display areas
        #matplotlib.pyplot.show(block=True)       # to display areas
        result = page.df
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 2000)
        pd.set_option('display.width', 500)
        result_dict = result.to_dict(orient = "index")
        if check_data(result_dict.items()):
            pages_list_raw.append(result_dict.items()) #this is list of dict_items
    return pages_list_raw

def check_data(page): #takes dict_items and check if page is needed
    """may be work with re???"""
    report = {"консолидированный отчет о финансовом положении": 1, "бухгалтерский баланс": 1, "консолидированный отчет о финансовом положении": 1,
              "консолидированный отчет о совокупном доходе": 1, "консолидированные отчеты о совокупном доходе": 1, "отчет о финансовых результатах": 1, "консолидированный отчет о прибылях и убытках и прочем совокупном доходе": 1,
              "консолидированный отчет о движении денежных средств": 1, "отчеты об изменениях капитала": 1, "консолидированные отчеты об изменениях капитала": 1,
              "консолидированный отчет об изменениях в капитале": 1, "отчет о движении денежных средств": 1, "консолидированные отчеты о движении денежных средств": 1,
              "консолидированный отчет о прибыли или убытке": 1,"консолидированные отчеты о прибылях или убытках": 1, "консолидированные отчеты о финансовом положении": 1,
              "консолидированный отчет о финансовом положении": 1, "консолидированный отчет о прибылях и убытках": 1, "консолидированный отчет о совокупном доходе": 1, 
              "консолидированный отчет о движении денежных средств": 1, "консолидированные отчеты о прибылях и убытках": 1
              }
    #for line in page:
    #    print(line)
    for _,line_info in page:
        if len(line_info.values()) <= 2: # to throw away pages without tables 
            return False
        for column in line_info.values():
            if column != "":
                if report.get(column.lower()):
                    return True
    return False

#TODO algo to now what actual number to get
def identify_info(ticker, pages_list_raw): #takes list with dicts and returns list of dicts. in dict info has format (info: [notes, year1, year2 ...]). Dict has 'Note' and 'LatestYear' keys to know in what column note is placed and where latest year is placed 
    pages_list = list()
    for page in pages_list_raw: 
        page_dict = dict()
        years_dict = dict()
        raw_line = list()
        last_line=list()
        note_column = -1
        """to make dicts more readable, to fix sentence"""
        for number, line_info in page:  #line looks like (number, {number1:column1, number2:column2 ...})
            line_info_list = list(line_info.values())
            number_of_columns = len(line_info_list)
            if ticker.measuring_unit == 0:  #to know measuring unit
                know_measure(ticker, line_info_list)
            #print(number, line_info)
            #print(line_info_list[0])
            if len([i for i in line_info.values() if i != ""]) == 1 and line_info_list[0] == '':  #if starts with ''
                raw_line.append("".join([i for i in line_info.values() if i != ""]))
                continue
            if len([i for i in line_info.values() if i != ""]) > 1 and line_info_list[0] == '':   #if starts with ''
                if len(raw_line):
                    for line in raw_line:
                        page_dict.setdefault(line, [""] * (number_of_columns-1))
                page_dict.setdefault(f"{number}", line_info_list[1:])
                raw_line.clear()
                continue
            if len([i for i in line_info.values() if i != ""]) == 1 and line_info_list[0][0].islower() != True:  #if starts with upper and rest empty
                raw_line.append(line_info_list[0])
                continue
            if len([i for i in line_info.values() if i != ""]) == 1 and line_info_list[0][0].islower():  #if starts with lower or ( and rest empty
                line = raw_line.pop(-1)
                raw_line.append(line +" " + line_info_list[0])
                continue
            if len([i for i in line_info.values() if i != ""]) > 1 and line_info_list[0][0].islower(): #if starts with lower or ( 
                for line in raw_line[:len(raw_line)-1]:
                    page_dict.setdefault(line, [""] * (number_of_columns-1))
                if len(raw_line):
                    page_dict.setdefault(raw_line[-1]+" "+line_info_list[0], line_info_list[1:])
                    last_line.append(raw_line[-1])      # to know the start of sentence when its x: -y; -z. to combine and make xy, xz.
                else:
                    page_dict.setdefault(last_line[0]+" "+line_info_list[0], line_info_list[1:])
                raw_line.clear()
                continue
            if len([i for i in line_info.values() if i != ""]) > 1 and line_info_list[0][0].isupper(): #if starts with upper 
                if len(raw_line):
                    for line in raw_line:
                        page_dict.setdefault(line, [""] * (number_of_columns-1))
                page_dict.setdefault(line_info_list[0], line_info_list[1:])
                raw_line.clear()
                last_line.clear()
                continue
        """to know where find the notes"""
        for value in page_dict.values():
            for i, line in enumerate(value):
                if know_notes(line):
                    note_column = i
                    #print(f"{note_column} for column {line}")
                    break
        """to know where find info by year"""
        for value in page_dict.values():
            for i, line in enumerate(value):
                if len(years_dict.items()) > 3:
                    break
                result = know_years(line)
                if result != None:
                    years_dict.setdefault(result.group(), i)
                    #print(f"{i} for column {result.group()}")
            if years_dict.items():
                last_year = max([int(i) for i in years_dict.keys()]) # last year in MSFO
        if note_column != -1:
            page_dict.setdefault("Note", note_column)
        else:
            page_dict.setdefault("Note", None)
        if len(years_dict.items()) != 0:
            page_dict.setdefault('LatestYear', years_dict[str(last_year)])
        else:
            page_dict.setdefault('LatestYear', None)
        pages_list.append(page_dict)
        #for k, v in page_dict.items():
        #    print(k ,v)
    return pages_list

def collect_data(ticker): #takes list of dicts and finds needed params
    #print("Find necessary data")
    viruchka_list = ["Выручка"]
    pribyl_list = ["Прибыль за год", "Чистая прибыль отчетного периода", "Прибыль за отчетный год"]
    for page in ticker.pages:
        if ticker.viruchka == 0:
            for name in viruchka_list:
                if page.get(name) != None:
                    latest_year = page['LatestYear'] #to know in what column in value-list latest year is placed (info: [notes, year1, year2 ...])
                    viruchka_str = page.get(name)[latest_year]
                    viruchka_raw = "".join(viruchka_str.split(","))
                    #print(ticker.measuring_unit)
                    viruchka = int(viruchka_raw) * ticker.measuring_unit
                    #print(f"Выручка - {ticker.viruchka}")
                    break
        if ticker.pribyl == 0:
            for name in pribyl_list:
                if page.get(name) != None and ticker.pribyl == 0:
                    pribyl_str = page.get(name)[latest_year]
                    pribyl_raw = "".join(pribyl_str.split(","))
                    #print(ticker.measuring_unit)
                    pribyl = int(pribyl_raw) * ticker.measuring_unit
                    #print(f"Прибыль - {ticker.pribyl}")
                    break
    return viruchka, pribyl

def know_notes(line): #checks if there notes
    notes_list = ["Примечание", "Поясн", "Прим", "Прим."]
    for word in notes_list:
        if line.find(word) >= 0:
            return True
    return False

def know_years(line): #checks if there years
    years_re = r"20\d\d"
    return re.search(years_re,line)

def know_measure(ticker, text):
    thousands = ["тыс.", "тыс", "тысячах", "thousands"]
    millions = ["млн.", "млн", "миллионах", "millions", "Млн"]
    for column in [i for i in text if i != ""]:
        for word in thousands:
            if column.find(word) >= 0:
                ticker.measuring_unit = 1000 #measuring unit
                break
        for word in millions:
            if column.find(word) >= 0:
                ticker.measuring_unit = 1000000 #measuring unit
                break
        
def print_pages(pages):
    print("___print_pages()_____")
    for page in pages:
        for line in page:
            print(line)
            print("____________________________")


def get_stock_exchange_price(name, method):
    if method == "p":
        price, amount = parser(name)
    if method == "t":
        price, amount = tinkoff_api(name)
    return (price, amount)

"""to get price and amount of shares from the internet. Using selenium to get all info because of javascript"""
def parser(name): 
    #print("Getting price and amount of shares")
    site_url = f"https://bcs-express.ru/kotirovki-i-grafiki/{name}"
    service = Service(executable_path=os.environ['ChromeDriverPath'])
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    page = webdriver.Chrome(service=service, options= options)
    page.implicitly_wait(2) # just to wait until page will load 
    page.get(site_url)
    price_sel = page.find_element(By.CLASS_NAME, 'Here.EWHp.Dlhk').text
    #print(price_sel)
    price = float(price_sel.replace(" ", "").replace(",", "."))
    amount_sel = page.find_elements(By.CLASS_NAME, 'rEKY')
    #print(amount_sel)
    amount = float(amount_sel[5].text.replace(" ", "").replace(",", "."))
    page.quit()
    return (price, amount)
 
def tinkoff_api(name):
    ticker_query_price = str()
    ticker_price_result = str()
    ticker_price_response = str()
    token = os.environ["TOKEN"]
    with Client(token) as client:
        ticker_query_price = client.instruments.find_instrument(query = name).instruments
        for i in ticker_query_price:
            if i.class_code == 'TQBR':
                ticker_data_choice = i
                break
        ticker_price_response = client.market_data.get_last_prices(figi = [ticker_data_choice.figi])
        ticker_query_amount = client.instruments.share_by(id_type = 1, id=ticker_data_choice.figi).instrument
        ticker_price_result = ticker_price_response.last_prices[0].price
        amount = ticker_query_amount.issue_size
        price = float(str(ticker_price_result.units) + "." + str(ticker_price_result.nano))
        return (price, amount)

"""using mysql"""
def write_db_mysql(ticker):
    if ticker.pe != 0 and ticker.ps != 0:
        try:
            with sql.connect(host="127.0.0.1", user = os.environ['MYSQL_user'], #input("Type user name: "), 
                             password = os.environ['MYSQL_password'], #getpass.getpass("Type password: "), 
                             database = "fm") as connection:
                query_select =  "SELECT * from fm_table"
                query_insert = "INSERT INTO fm_table (ticker, revenue, income, pe, ps, amount, price, cap) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                with connection.cursor() as cursor:
                    #to see columns
                    cursor.execute("desc fm_table")
                    print_db_mysql([column[0] for column in cursor.fetchall()])   
                    #to add data
                    data = (ticker.name, ticker.viruchka, ticker.pribyl, ticker.pe,
                           ticker.ps, ticker.amount, ticker.price, ticker.capitalization)
                    cursor.execute(query_insert, data)
                    connection.commit()
                    #to print all lines
                    cursor.execute(query_select)
                    result = cursor.fetchall()
                    for line in result:
                        print_db_mysql(line)
        except sql.Error as e:
            print(e)

"""To check if the data is already available in db"""
def check_db_postsql(url):
    conn = psql.connect(os.environ["PSQL"])
    cur = conn.cursor()
    cur.execute("select * from ticker_info where url = %s", (url,))
    result = cur.fetchone()
    if result != None:
        ps = float(result[-1])
        pe = float(result[-2])        
        print("Data is already available")
        print(pe, ps)
        return pe, ps
    else:
        return None

"""using postgresql"""
def write_db_postsql(ticker):
    conn = psql.connect(os.environ["PSQL"])
    cur = conn.cursor()
    # Execute a query
    cur.execute("INSERT into ticker_info (url, name, pribyl, viruchka, price, amount, measuring_unit, pe, ps) VALUES \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)",\
                (ticker.url, ticker.name, ticker.pribyl, ticker.viruchka, ticker.price, ticker.amount, ticker.measuring_unit, ticker.pe, ticker.ps))
    conn.commit()
    cur.close()
    conn.close() 

def read_db_postsql():
    conn = psql.connect(os.environ["PSQL"])
    cur = conn.cursor()
    cur.execute("select * from ticker_info")
    records = cur.fetchall()
    print(records)
    cur.close()
    conn.close()

def print_db_mysql(line):
    for i in line:
        print(f'{i:<18}',end = "")
    print(end="\n")

def analyze_data(ticker): #just do the math
    ticker.capitalization = ticker.price * ticker.amount
    if ticker.pribyl != 0:
        pe = ticker.capitalization / ticker.pribyl
    if ticker.viruchka != 0:
        ps= ticker.capitalization / ticker.viruchka
    return pe, ps

def timetrack(func):
    def count_time(*arg):
        start_time = time.time() #checking how long code executes
        result = func(*arg)
        print(f"--- {time.time() - start_time} seconds ---")
        return result
    return count_time

@timetrack
def run(url, name, method = 'p'):#just run the program
    ticker = Ticker(url, name)
    check = check_db_postsql(ticker.url) 
    if check:
        return check
    file = get_file(ticker.url, ticker.name) 
    pages_raw = read_content(file)
    ticker.pages = identify_info(ticker, pages_raw)
    ticker.viruchka, ticker.pribyl = collect_data(ticker)
    ticker.price, ticker.amount = get_stock_exchange_price(ticker.name, method)
    ticker.pe, ticker.ps = analyze_data(ticker)
    ticker.print_ticker_data()
    write_db_postsql(ticker)
    return (ticker.pe, ticker.ps)

if __name__ == "__main__":
    name = 'mtss'
    run(docs[1], name, 't')
    

