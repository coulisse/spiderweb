#**********************************************************************************
# plot qso trend
#**********************************************************************************
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
import matplotlib.dates as mdates
from qry import query_manager
from plotuty import saveplt
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing
#from statsmodels.tsa.holtwinters import SimpleExpSmoothing  
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning

logging.config.fileConfig("../cfg/plots_log_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
file_output = '../static/plots/'+ os.path.splitext(os.path.basename(sys.argv[0]))[0]

logger.info("Start")
logger.info("doing query...")

#construct final query string
qry_string="""
 select     
	FROM_UNIXTIME(time,'%Y-%m-%d') as day,                 
	count(0) as total         
	from spot                 
	WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 60 MONTH)                 
	GROUP by 1
;
    """
logger.debug(qry_string) 
qm=query_manager()
qm.qry_pd(qry_string)
df=qm.get_data()
logger.info("query done")
logger.debug (df)  

if df is None ==0:
    logger.warning("no data found")
    sys.exit(1)
logger.info("plotting...")

warnings.simplefilter('ignore', ConvergenceWarning)
df['day']=pd.to_datetime(df['day'])
df=df.set_index('day')
df=df.resample('D').interpolate(method='pad', limit_direction='forward', axis=0)
df=df.rolling('30D').mean()
y=df['total']
plt.style.use('seaborn-colorblind')
fig, ax = plt.subplots(figsize=(14,3))
plt.suptitle("QSO trend")
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
plt.annotate('created on '+dt_string, (0,0), (0, -20), xycoords='axes fraction', textcoords='offset points', va='top', size=8, style='italic')    
plt.xlabel("Time")
plt.ylabel("QSO")
plt.margins(0)
plt.grid(True)
plt.grid(which='major', color='grey', linestyle=':', linewidth=1)
plt.subplots_adjust(left=0.15)
ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.plot(y,marker='', linestyle='-', color='#4089F9', linewidth=1,  label='observed')
ax.fill_between(df.index, y, facecolor='#4089F9', alpha=0.4)
model = ExponentialSmoothing(y, seasonal_periods =52, trend='add', seasonal='add', damped_trend=True)
#model = SimpleExpSmoothing(y, trend='add', seasonal='add', damped_trend=True)
fit=model.fit()
fcast = fit.forecast(40)
ax.plot(fcast,marker='',linestyle='-', color='#23B55E', linewidth=1, label='predicted')
logger.debug(fcast)
ax.fill_between(fcast.index,fcast,facecolor='#23B55E',alpha=0.4)

# Minor ticks every month.
fmt_month = mdates.MonthLocator()
ax.xaxis.set_minor_locator(fmt_month)
ax.legend()
saveplt(plt,file_output)

logger.info("End")

