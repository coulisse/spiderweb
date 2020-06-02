import MySQLdb as my  
import logging          
import json


logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)s]: %(message)s',datefmt='%m/%d/%Y %I:%M:%S')


def qry(qs):
    try:
        with open('../cfg/config.json') as json_data_file:
            cfg = json.load(json_data_file)
    except Exception as e1:
        logging.error(e1)
        return         

    try:
        db = my.connect(host=cfg['mysql']['host'],
               user=cfg['mysql']['user'],
               passwd=cfg['mysql']['passwd'],
               db=cfg['mysql']['db']
            )
        cursor = db.cursor()
        number_of_rows = cursor.execute('''SET NAMES 'utf8';''')
        cursor.execute(qs)
        rv=cursor.fetchall()
        cursor.close()
    except Exception as e2:
        logging.error(e2)

    finally:
        db.close()
        return rv
