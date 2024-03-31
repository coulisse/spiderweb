# *****************************************************************************************
# module used to make query to mariadb
# TODO: manage polymorfism and use only one qry sign
# *****************************************************************************************
# import MySQLdb as my
import mariadb as my
import logging
import json
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
)


class query_manager:
    # connection definition

    def __init__(self):
        try:
            with open("../cfg/config.json") as json_data_file:
                cfg = json.load(json_data_file)
        except Exception as e1:
            logging.info(e1)
            logging.info("trying with other path...")
            try:
                with open("cfg/config.json") as json_data_file:
                    cfg = json.load(json_data_file)
            except Exception as e2:
                logging.error(e2)
                return

        logging.info("config file loaded")


        self.__cnxpool = my.ConnectionPool(
            host=cfg["mysql"]["host"],
            user=cfg["mysql"]["user"],
            passwd=cfg["mysql"]["passwd"],
            db=cfg["mysql"]["db"],
            pool_name="spider_pool",
            pool_size=5,
            pool_validation_interval=250
        )


        logging.info("db connection pool created")

    # normal query
    def qry(self, qs, prepared_statement=False):
        try:
            cnx = self.__cnxpool.get_connection()
            cursor = cnx.cursor(prepared=prepared_statement)
            cursor.execute(qs)
            self.__data = cursor.fetchall()
            self.__row_headers = [
                x[0] for x in cursor.description
            ]  # this will extract row headers
            cursor.close()
        except Exception as e2:
            logging.error(e2)
        finally:
            cnx.close()

    def get_data(self):
        return self.__data

    def get_headers(self):
        return self.__row_headers

    # query with pandas
    def qry_pd(self, qs):
        try:
            cnx = self.__cnxpool.get_connection()
            self.__data = pd.read_sql(qs, con=cnx)
        except Exception as e2:
            logging.error(e2)
        finally:
            cnx.close()
