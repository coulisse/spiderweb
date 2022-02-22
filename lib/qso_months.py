#*****************************************************************************************
# plot qso per months                                      
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
import matplotlib.gridspec as gridspec
from qry import query_manager
from plotuty import saveplt
from calendar import monthrange

logging.config.fileConfig("../cfg/plots_log_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
file_output = '../static/plots/'+ os.path.splitext(os.path.basename(sys.argv[0]))[0]

logger.info("Start")
logger.info("doing query...")

#construct final query string
qry_string="""
select month(s1.ym) as referring_month, 
	sum(
		case 
			when YEAR(s1.ym)=YEAR(now()) 
			then s1.total 
			else 0
		end
		) as current_year,
	sum(
		case 
			when YEAR(s1.ym)=YEAR(now())-1 
			then s1.total 
			else 0
		end
		) as one_year_ago,
	sum(
		case 
			when YEAR(s1.ym)=YEAR(now())-2 
			then s1.total 
			else 0
		end
		) as two_year_ago		
	from (
		/* extract number of qso per year */
		select 
			CAST(
				CONCAT(
					YEAR(FROM_UNIXTIME(time)),		
					'-',
					right(concat('0',MONTH(FROM_UNIXTIME(time))),2),   
					'-',
					'01'
					)
				AS DATE) as ym,
				count(0) as total
			from spot 
				WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 36 MONTH)
				GROUP by 1
				/*union used to initialize all months */
				union select '1976-01-01', 0        
				union select '1976-02-01', 0         
				union select '1976-03-01', 0       
				union select '1976-04-01', 0
				union select '1976-05-01', 0
				union select '1976-06-01', 0
				union select '1976-07-01', 0
				union select '1976-08-01', 0
				union select '1976-09-01', 0
				union select '1976-10-01', 0
				union select '1976-11-01', 0
				union select '2019-12-01', 0          
	) as s1
	group by referring_month
;
    """
logger.debug(qry_string) 
qm=query_manager()
qm.qry(qry_string)
data=qm.get_data()

logger.info("query done")
logger.debug (data)  

if data is None or len(data)==0:
    logger.warning("no data found")
    sys.exit(1)
logger.info("plotting...")


months, current_year, one_year_ago, two_year_ago = zip(*data)
#plt.style.use('seaborn-colorblind')
#plt.style.use('fast')
#plt.style.use('seaborn-bright')
plt.style.use('tableau-colorblind10')
fig, ax = plt.subplots()
ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.suptitle("QSO per month")
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
plt.annotate('created on '+dt_string, (0,0), (0, -20), xycoords='axes fraction', textcoords='offset points', va='top', size=8, style='italic')    
plt.xticks(rotation=90)
plt.xlabel("Months")
plt.ylabel("QSO")
plt.grid(False)
plt.subplots_adjust(left=0.15)

width=0.30
#plot current year and estimate trend of last month
current_year_lst = list(current_year)
le=len(current_year_lst)-1
day=datetime.today().day
month=datetime.today().month
year=datetime.today().year
days_of_month=monthrange(year,month)
current_year_lst[month-1]=int(current_year[month-1]/day*days_of_month[1])
plt.bar(months[month-1], tuple(current_year_lst),width=width, align='edge', color='lightsteelblue')
plt.bar(months,current_year,width=width, align='edge',label=year)

#plot previous year
#calculate position of bar of previous year
months1=[]
for i in months:
    months1.append(i-width)
plt.bar(months1,one_year_ago,width=width, align='edge',label=year-1)

#plot two years ago
#calculate position of bar of two years ago
months2=[]
for i in months1:
    months2.append(i-width)
plt.bar(months2,two_year_ago,width=width, align='edge',label=year-2)

#plot legend and set ticks frequency (every one month)
plt.legend()
plt.xticks(np.arange(min(months), max(months)+1, 1.0),rotation='horizontal')

saveplt(plt,file_output)

logger.info("End")
