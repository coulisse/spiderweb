# *****************************************************************************************
# module used to make query to mariadb
# *****************************************************************************************
import mariadb as my
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class query_manager:
    # connection definition
    def __init__(self, cfg):
        self.__data = dict()
        self.__row_headers = dict()
        self.__cnxpool = None

        try:
            self.__cnxpool = my.ConnectionPool(
                host=cfg["mysql"]["host"],
                user=cfg["mysql"]["user"],
                passwd=cfg["mysql"]["passwd"],
                db=cfg["mysql"]["db"],
                pool_name="spider_pool", # Il nome del pool
                pool_size=5,
                pool_validation_interval=250
            )
            logger.info("DB connection pool 'spider_pool' created.")
        except Exception as e:
            logger.error(f"Error creating DB connection pool: {e}")
            self.__cnxpool = None 

    #used to close connection pool
    def close(self):
        if self.__cnxpool:
            try:
                self.__cnxpool.close()
                logger.info("DB connection pool 'spider_pool' closed.")
            except Exception as e:
                logger.warning(f"Error closing DB connection pool 'spider_pool': {e}")
            finally:
                self.__cnxpool = None 

    # normal query
    def qry(self, qs, prepared_statement=False):
        if self.__cnxpool is None:
            logger.error("No DB connection pool available! Cannot execute query.")
            self.__data = []
            self.__row_headers = []
            return
        cnx = None
        self.__data = dict()
        self.__row_headers = dict()
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
            logger.error(e2)
        finally:
            if cnx is not None:
                cnx.close()

    def get_data(self):
        return self.__data

    def get_headers(self):
        return self.__row_headers

    # query with pandas
    def qry_pd(self, qs):
        if self.__cnxpool is None:
            logger.error("No DB connection pool available! Cannot execute query_pd.")
            self.__data = pd.DataFrame()
            self.__row_headers = []
            return
        self.__data = pd.DataFrame()
        self.__row_headers = dict()
        cnx = None
        try:
            cnx = self.__cnxpool.get_connection()
            self.__data = pd.read_sql(qs, con=cnx)
        except Exception as e2:
            logger.error(e2)
        finally:
            if cnx is not None:
                cnx.close()