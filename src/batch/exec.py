import datetime as dt
from sql import *
from scrape import *

import logging
import sys
import os
import argparse

app_home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)) , "../.." ))
sys.path.append(os.path.join(app_home))



def exec_scrape_update():
    #####################################
    # Logger Setting
    #####################################
    prog = os.path.splitext(os.path.basename(__file__))[0]


    log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)

    logger.addHandler(stdout_handler)

    today = dt.datetime.now()
    today = today.strftime('%Y%m%d%H%M%S')

    log_path = os.path.join(app_home, 'log', 'batch', 'scrape', 'update', prog + "_" + str(today) + ".log")
    logging.basicConfig(filename=log_path, level=logging.INFO)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    #####################################
    # Scraping
    #####################################
    
    try:
        scrape_code = get_listing_code()

        for code, last_update_date in scrape_code.items():
            # scrape
            bs = scrape_nikkei(code)
            if bs is None:
                logger.error(f"invalid url {code}")
                continue

            # transfer
            df = transform_nikkei(bs, last_update_date, code)

            if df is None:
                logger.error(f"invalid html {code}")
                continue

            if df is False:
                logger.info(f"no listing {code}")
                if not(update_listing_flg(code)):
                    logger.error(f"failed no listing {code}")
                continue

            if len(df) == 0:
                logger.error(f"no update {code}")
                continue
            
            # set db
            if not(update_stock_history(code, df)):
                logger.error(f"There are bug {code}")


        # notification
        
    except Exception as e:
        logger.exception(e)
        sys.exit(1)

def exec_scrape_register():
    #####################################
    # Logger Setting
    #####################################
    prog = os.path.splitext(os.path.basename(__file__))[0]


    log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)

    logger.addHandler(stdout_handler)

    today = dt.datetime.now()
    today = today.strftime('%Y%m%d%H%M%S')

    log_path = os.path.join(app_home, 'log', 'batch', 'scrape', 'register', prog + "_" + str(today) + ".log")
    logging.basicConfig(filename=log_path, level=logging.INFO)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    #####################################
    # Scraping
    #####################################
    
    try:
        bs = scrape_nikkei("ipo")
        df = transform_nikkei_ipo(bs)
        if update_ipo(df):
            logging.info("success")
        else:
            logging.error("error")

    except Exception as e:
        logger.exception(e)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='scrape')
    parser.add_argument('--method', '-m', help='u:update or r: register', default='u')
    args = parser.parse_args()
    
    method=args.method

    if method=="u":
        exec_scrape_update()
    elif method=="r":
        exec_scrape_register()


if __name__ == '__main__':
    main()