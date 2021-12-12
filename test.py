import os
import flask
from flask import request, render_template, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_minify import minify
import json
import time, threading
import logging
import logging.config
from lib.dxtelnet import who
from lib.adxo import get_adxo_events
from lib.qry import query_manager
from lib.cty import prefix_table
__author__ = 'IU1BOW - Corrado'


logging.config.fileConfig("cfg/webapp_log_config.ini", disable_existing_loggers=True)
logger = logging.getLogger(__name__)
logger.info("Start")


#define country table for search info on callsigns
pfxt=prefix_table()


#create object query manager
qm=query_manager()

ctrok=0
ctrko=0
ctrtotal=0

query_string="SELECT * from dxcluster.spot limit 100000;"
qm.qry(query_string)
row_headers=qm.get_headers()
data=qm.get_data()
logger.info("query done")

if data is None or len(data)==0:
    logger.warning("no data found")

for result in data:
    main_result=dict(zip(row_headers,result)) 
    try:
        search_prefix=pfxt.find(main_result["spotcall"])         
#        if int(main_result["spotcq"]) == int(search_prefix["cq"]):
        if int(main_result["spotitu"]) == int(search_prefix["itu"]):
            ctrok+=1
        else:
            ctrko+=1
#            print (main_result, search_prefix)
#            logger.warning("rowid: "+str(main_result["rowid"])+" spotcall: "+(main_result["spotcall"])+"  "+str(main_result["spotcq"]) + " != " + str(search_prefix["cq"]))
            logger.warning("rowid: "+str(main_result["rowid"])+" spotcall: "+(main_result["spotcall"])+"  "+str(main_result["spotitu"]) + " != " + str(search_prefix["itu"]))
        ctrtotal+=1

    except Exception as e:
         logger.error(e)


logger.info("equal......: "+str(ctrok))
logger.info("not equal..: "+str(ctrko))
logger.info("total......: "+str(ctrtotal))
logger.info("end")



