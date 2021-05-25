#*****************************************************************************************
# plot qso per hour / band                                 
#*****************************************************************************************
__author__ = 'IU1BOW - Corrado'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
import os 
from datetime import datetime
import logging
import logging.config 
import json
import matplotlib.gridspec as gridspec 
from qry import query_manager
from plotuty import saveplt
from matplotlib.colors import LogNorm
from calendar import monthrange

logging.config.fileConfig("../cfg/plots_log_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
file_output = '../static/plots/'+ os.path.splitext(os.path.basename(sys.argv[0]))[0]

#load band file
with open('../cfg/bands.json') as json_bands:
        band_frequencies = json.load(json_bands)


logger.info("Start")
logger.info("doing query...")

#construct bands query
bands_qry_string = 'CASE '
for i in range(len(band_frequencies["bands"])):
    bands_qry_string+=' WHEN freq between '+str(band_frequencies["bands"][i]["min"])+' AND '+ str(band_frequencies["bands"][i]["max"])
    bands_qry_string+=' THEN "'+band_frequencies["bands"][i]["id"]+'"'


#construct bands query weight
bands_weight_qry_string = 'CASE '
for i in range(len(band_frequencies["bands"])):
    bands_weight_qry_string+=' WHEN freq between '+str(band_frequencies["bands"][i]["min"])+' AND '+ str(band_frequencies["bands"][i]["max"])
    bands_weight_qry_string+=' THEN "'+str(band_frequencies["bands"][i]["min"])+'"'

   
#construct final query string
qry_string ="""
select s1.hour, s1.band, s1.total from (
	SELECT 
             cast(concat(HOUR (FROM_UNIXTIME(time))) as unsigned) as hour,
             """+bands_qry_string+""" ELSE "other" END as band,
             cast("""+bands_weight_qry_string+""" ELSE 0 END as unsigned) as band_weight,
             cast(round(count(0)/20) as unsigned) AS total
	from spot 
            WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 1 MONTH)
            and rowid > (select max(rowid)-500000 from spot) 
	    group by 1, 2
        ) as s1
        order by s1.band_weight
      ; 
"""

logger.debug(qry_string)
qm=query_manager()
qm.qry(qry_string)
data=qm.get_data()

logger.info("query done")
logger.debug (data)

#plot
if data is None or len(data)==0:
    logger.warning("no data found")
    sys.exit(1)
logger.info("plotting...")


#main
x, y, z = zip(*data)
fig, ax = plt.subplots()
plt.suptitle("QSO per hour in last month")
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
plt.annotate('created on '+dt_string, (0,0), (0, -20), xycoords='axes fraction', textcoords='offset points', va='top', size=8, style='italic')    
plt.xticks(rotation=90)
plt.xlabel("Hours")
plt.ylabel("QSO")
plt.grid(False)
plt.subplots_adjust(left=0.15)

plt.scatter(x, y, z, c=x, cmap='jet', edgecolors='darkslategray', alpha=0.5, )
plt.xticks(np.arange(1, 24, 2.0),rotation='horizontal')

saveplt(plt,file_output)


logger.info("End")

