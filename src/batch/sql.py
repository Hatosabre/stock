import sqlite3
from contextlib import closing
import datetime as dt
import os
import pandas as pd

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)) , "../.." ))
DB = os.path.join(app_home, "data/db/nikkeiscrape.db")

def select(sql):
    with closing(sqlite3.connect(DB)) as conn:
        try:
            c = conn.cursor()
            req = c.execute(sql)
            stock_update_info = dict()
            for code, last_date in req:
                last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
                stock_update_info[code] = last_date
        except sqlite3.Error:
            return None
    return stock_update_info

def get_listing_code():
    sql = 'select code, last_date from sec_main where ipo_flag = 0 order by code ASC'
    req = select(sql)
    return req

def update_listing_flg(code):
    with closing(sqlite3.connect(DB)) as conn:
        try:
            c = conn.cursor()
            sql = f'update sec_main set ipo_flag = 1 where code = ?'
            c.execute(sql, [(code)])
            conn.commit()
        except sqlite3.Error as e:
            print(e)
            return False
    return True

def update_stock_history(code, cdf):
    with closing(sqlite3.connect(DB)) as conn:
        try:
            c = conn.cursor()

            sql_create_stock = f'create table if not exists code_{code} (date primary key,open int,high int,low int,close int,adj_close int,volume int)'
            c.execute(sql_create_stock)

            sql_update_stock = f'replace into code_{code} (date,open,high,low,close,adj_close,volume) values (?,?,?,?,?,?,?)'
            cdf = cdf[["date", "open", "high", "low", "close", "adj_close", "volume"]]
            info = cdf.values.tolist()
            c.executemany(sql_update_stock, info)

            sql_update_last_date = 'update sec_main set last_date = ? where code = ?'
            last_date = cdf["date"].max()
            last_date = last_date.strftime('%Y-%m-%d')
            c.executemany(sql_update_last_date, [(last_date, code, )])

            conn.commit()
        except sqlite3.Error as e:
            print(e)
            return False
    return True

def update_ipo(cdf):
    with closing(sqlite3.connect(DB)) as conn:
        try:
            c = conn.cursor()

            sql_select = 'select * from sec_main'
            sql_update = 'replace into sec_main (code,sec_name,sec_place,ipo_flag,last_date) values (?,?,?,0,"1970-01-01")'

            registered_code = pd.read_sql_query(sql_select, conn)
            info = cdf[~cdf['code'].isin(registered_code['code'].values.tolist())]
            info = info.values.tolist()

            c.executemany(sql_update, info)
            conn.commit()
        except sqlite3.Error:
            return None
    return True
