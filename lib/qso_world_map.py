#*****************************************************************************************
# plot qso on a world map                                  
#*****************************************************************************************
#https://datascientyst.com/plot-latitude-longitude-pandas-dataframe-python/
__author__ = 'IU1BOW - Corrado'
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os 
from datetime import datetime
import logging
import logging.config 
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from qry import query_manager
from plotuty import saveplt
from cty import prefix_table

logging.config.fileConfig("../cfg/plots_log_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
file_output = '../static/plots/'+ os.path.splitext(os.path.basename(sys.argv[0]))[0]

logger.info("Start")
logger.info("doing query...")

#construct final query string
qry_string ="""
select spotcall as dx
from  spot    
WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 1 MONTH)
and rowid > (select max(rowid)-500000 from spot) 
group by 1;
"""

logger.debug(qry_string)
qm=query_manager()
qm.qry(qry_string)
data=qm.get_data()
row_headers=qm.get_headers()

logger.info("query done")
del qm
logger.debug (data)
#plot
if data is None or len(data)==0:
    logger.warning("no data found")
    sys.exit(1)

#define country table for search info on callsigns
pfxt=prefix_table()
df = pd.DataFrame(columns=['row_id','dx','lat','lon'])
dx=[]
lat=[]
lon=[]
row_id=[]
idx=0
#count=[]
for result in data:
    main_result=dict(zip(row_headers,result)) 
    # find the country in prefix table
    search_prefix=pfxt.find(main_result["dx"])         
    if search_prefix["country"] != "unknown country" :
    # merge recordset and contry prefix 
       dx.append(main_result["dx"])
       lon.append(float(search_prefix["lat"]))
       lat.append(-float(search_prefix["lon"]))
       idx+=1
       row_id.append(idx)

del pfxt
df['dx']=dx
df['lat']=lat
df['lon']=lon
df['row_id']=row_id
df_grp=df.groupby(["lat", "lon"])["row_id"].count().reset_index(name="count")
logger.info("plotting...")


#main
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
#fig, ax = plt.subplots(figsize = (18,6))
fig, ax = plt.subplots(figsize = (14,7))
plt.suptitle("World QSO in last month")
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
plt.annotate('created on '+dt_string, (0,0), (0, -20), xycoords='axes fraction', textcoords='offset points', va='top', size=8, style='italic')    
plt.grid(False)
plt.margins(0.0)
#water = 'lightskyblue'
#water = 'skyblue'
water = 'lightsteelblue'
earth = 'cornsilk'
ax.set_aspect('equal')
ax.set_facecolor(water)
geometry=gpd.points_from_xy(df_grp.lat, df_grp.lon)
gdf = GeoDataFrame(df_grp, geometry=geometry)
world= gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
world.plot(ax=ax,color=earth,edgecolor='grey')

gdf.plot(column='count', ax=ax,alpha=0.2, markersize=gdf['count'])
logger.debug(gdf.head)

saveplt(plt,file_output)

logger.info("End")

#os._exit(0)
