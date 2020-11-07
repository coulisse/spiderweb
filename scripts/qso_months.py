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
import matplotlib.gridspec as gridspec
from qry import *
from plotuty import saveplt
from calendar import monthrange

logging.config.fileConfig("../cfg/log_config.ini", disable_existing_loggers=False)
file_output = '../static/plots/'+ os.path.splitext(os.path.basename(sys.argv[0]))[0]

logging.info("Start")
logging.info("doing query...")

#construct final query string
qry_string="""

	select 
		concat(YEAR(FROM_UNIXTIME(time)),'-',  
		right(concat('0',MONTH(FROM_UNIXTIME(time))),2)
                ) as ym, 
		count(0) as number
		from spot 
		GROUP by 1
                ORDER by 1;

    """
logging.debug(qry_string) 
data=qry(qry_string)

logging.info("query done")
logging.debug (data)  

if data is None or len(data)==0:
    logging.warning("no data found")
    sys.exit(1)
logging.info("plotting...")


x, y = zip(*data)
plt.style.use('seaborn-colorblind')
fig, ax = plt.subplots()
ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.suptitle("QSO per months")
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
plt.annotate('created on '+dt_string, (0,0), (0, -60), xycoords='axes fraction', textcoords='offset points', va='top', size=8, style='italic')    
plt.xticks(rotation=90)
plt.xlabel("Months")
plt.ylabel("QSO")
plt.grid(False)
plt.subplots_adjust(left=0.15)

plt.bar(x, y, align='center')
list_y = list(y)
le=len(list_y)-1
day=datetime.today().day
month=datetime.today().month
year=datetime.today().year
days_of_month=monthrange(year,month)
list_y[le]=int(y[le]/day*days_of_month[1])
y = tuple(list_y)
plt.scatter(x,y)

saveplt(plt,file_output)


logging.info("End")


