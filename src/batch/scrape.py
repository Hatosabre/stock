from bs4 import BeautifulSoup
from urllib import request, error
import requests
import pandas as pd
import datetime as dt
import logging
import os
import sys
from utils import *

log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(log_format)

logger.addHandler(stdout_handler)

NIKKEI255_PATH = "https://www.nikkei.com/markets/worldidx/chart/nk225/"
NIKKEI_PATH = "https://www.nikkei.com/nkd/company/history/dprice/"
NIKKEI_IPO_PATH = "https://www.nikkei.com/markets/kigyo/ipo/money-schedule/"

def scrape_nikkei(code: str="0000") -> BeautifulSoup:
    if code == "0000":
        scrape_path = NIKKEI255_PATH
    elif code == "ipo":
        scrape_path = NIKKEI_IPO_PATH
    else:
        scrape_path = NIKKEI_PATH + "?scode={}".format(code)
    
    try:
        logging.info(f"start scrape {code}")
        page_html = request.urlopen(url=scrape_path, timeout=60)
        logging.info(f"finish scrape {code}")
    except error.HTTPError as e:
        logging.exception(e)
        return None
    except error.URLError as e:
        logging.exception(e)
        return None

    page_html_data = BeautifulSoup(page_html, 'html.parser', from_encoding='UTF-8')
    
    return page_html_data

def transform_nikkei(bs: BeautifulSoup, last_update_date: dt.datetime, code: str) -> pd.DataFrame:
    logging.info(f"start transform {code}")
    
    stock_history = bs.find_all("table", {"class": "w668"})

    if len(stock_history) == 0:
        non_listing_flg = bs.find("div", {"class": "m-breadcrumb"})
        if non_listing_flg is None:
            return None
        non_listing_flg = non_listing_flg.get_text()
        if "非上場" in non_listing_flg:
            return False
        return None
    
    stock = stock_history[0]
    tr_list = stock.find_all('tr')

    stocks = pd.DataFrame()

    for tr in tr_list:
        date = tr.find("th", {"class": "a-taC"}).string.strip()
        if date == '日付':
            continue

        stock_values = []

        if date[-1] == '#':
            date = date[:-4]
        else:
            date = date[:-3]
        
        date = convert_date(date)

        if date < last_update_date:
            continue
        
        stock_values.append(date)
        
        td_list = tr.find_all('td')

        for td in td_list:
            td_value = td.string.replace(",", "")
            if td_value == '--':
                break
            stock_values.append(float(td_value))
            stock_df = pd.DataFrame(stock_values)
        else:
            stocks = pd.concat([stocks, stock_df], axis=1)

    
    if len(stocks) == 0:
        return stocks
    stocks = stocks.T
    stocks.columns = ["date", "open", "high", "low", "close",  "volume", "adj_close"]
    logging.info(f"finish transform {code}")

    return stocks

def transform_nikkei_ipo(bs: BeautifulSoup) -> pd.DataFrame:
    div_m_block = bs.find_all("div", {"class": "m-block"})
    for div in div_m_block:
        year = div.find("h3", {"class": "paddingB0"}).string.strip()[:-1]
        year = int(year)
        tbody_list = div.find_all("tbody")
        ipo_info_df = pd.DataFrame()
        for tbody in tbody_list:
            tr_list = tbody.find_all("tr")

            for tr in tr_list:
                th = tr.find("th")
                if th is None:
                    break
                th = th.string.strip()

                if th == "上場日" or th == "":
                    continue
                if (dt.datetime.now() + dt.timedelta(days=7) <= convert_date(th, year=year)) or (dt.datetime.now() > convert_date(th, year=year)):
                    continue

                td_list = tr.find_all("td")
                security_code = td_list[0].find("a").string
                company_name = td_list[1].find("a").string
                security_place = td_list[4].string.strip()
                if security_place in ("札証アンビシャス", "TOKYO PRO", "福証Ｑボード"):
                    continue

                ipo_info = pd.DataFrame([security_code, company_name, security_place])
                ipo_info_df = pd.concat([ipo_info_df, ipo_info], axis=1)
    
    if len(ipo_info_df) == 0:
        return None
    print(ipo_info_df)
    ipo_info_df = ipo_info_df.T
    ipo_info_df.columns = ["code", "company_name", "security_place"]
    
    return ipo_info_df




