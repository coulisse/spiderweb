#*****************************************************************************************
# plot propagation heat maps                               
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
from matplotlib.colors import LogNorm
import json

logging.config.fileConfig("../cfg/plots_log_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
file_output = '../static/plots/'+ os.path.splitext(os.path.basename(sys.argv[0]))[0]


#load band file
with open('../cfg/bands.json') as json_bands:
        band_frequencies = json.load(json_bands)

#load continent file
with open('../cfg/continents.json') as json_continents:
        continents_cq = json.load(json_continents)

logger.info("Start")
logger.info("doing query...")

#construct bands query
bands_qry_string = 'CASE '
for i in range(len(band_frequencies["bands"])):
    bands_qry_string+=' WHEN freq between '+str(band_frequencies["bands"][i]["min"])+' AND '+ str(band_frequencies["bands"][i]["max"])
    bands_qry_string+=' THEN "'+band_frequencies["bands"][i]["id"]+'"'

#construct continent region query
spottercq_qry_string = 'CASE '
spotcq_qry_string = 'CASE '
for i in range(len(continents_cq["continents"])):
    spottercq_qry_string+=' WHEN spottercq in('+continents_cq["continents"][i]["cq"]+')'
    spottercq_qry_string+=' THEN "' +continents_cq["continents"][i]["id"]+'"'
    spotcq_qry_string+=' WHEN spotcq in('+continents_cq["continents"][i]["cq"]+')'
    spotcq_qry_string+=' THEN "' +continents_cq["continents"][i]["id"]+'"'

#construct final query string
qry_string ="""
	SELECT 
	       	"""+spottercq_qry_string+""" ELSE spottercq END,
                """+spotcq_qry_string+""" ELSE spotcq END,
                """+bands_qry_string+""" END,
                count(0) number
	from spot 
        where
            rowid > (select max(rowid) max_rowid from spot) - 5000 and
            time > UNIX_TIMESTAMP()-3600
        group by 1, 2, 3
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

#preparing data

continents=continents_cq["continents"]
bands=band_frequencies["bands"]


continents_ar=[]
for i, item_continent in enumerate(continents):
    continents_ar.append(item_continent["id"])

bands_ar=[]
for i, item_band in enumerate(bands):
    bands_ar.append(item_band["id"])

# fucntion for search continent in the global data returned by query and making a cartesian product
# in order to prepare data for heatmap
def filter_de(data_list,continent,continents_list, band_list):
    data_filtered=[]
    for i, item_data in enumerate(data_list):
        if item_data[0]==continent and not (item_data[3] is None):
            element=[]
            element.append(item_data[1])
            element.append(item_data[2])
            element.append(item_data[3])
            data_filtered.append(element)

    cartesian_product = []
    for j, item_continent in enumerate(continents_list):
        for k, item_band in enumerate(band_list): 
            found=0
            for l, item_filtered in enumerate(data_filtered):
                if item_filtered[0]==item_continent["id"] and item_filtered[1]==item_band["id"]:
                    cartesian_product.append(item_filtered)
                    found=1
            if found==0:
                element=[]
                element.append(item_continent["id"])
                element.append(item_band["id"])
                element.append(0)
                cartesian_product.append(element)

    logger.debug("cartesian product for continent: "+continent)
    logger.debug(cartesian_product)
    return cartesian_product

#main
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
for i, item in enumerate(continents):
    continent=item["id"]
    data_de=filter_de(data,continent,continents,bands)
    dx, band, number=zip(*data_de)

    number_ar = []
    for j in range(0, len(number), len(bands)):
        number_ar.append(number[j : j+len(bands)])

    logger.debug("heatmap:")
    logger.debug(np.array(number_ar))

    LOGMIN = 0.1
    im = plt.imshow(np.array(number_ar), cmap='YlOrRd', interpolation='quadric', norm=LogNorm(vmin=10, vmax=35),vmin=max(np.array(number_ar).min(), LOGMIN))
    for spine in plt.gca().spines.values():
            spine.set_visible(False)

    plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='on', labelbottom='on')
    plt.gca().set_xticks(np.arange(len(bands)))
    plt.gca().set_yticks(np.arange(len(continents)))
    plt.gca().set_yticklabels(continents_ar, fontsize=8)
    plt.gca().set_xticklabels(bands_ar, fontsize=8)
    plt.gca().set_xticks(np.arange(.5,len(bands),1),minor=True) 
    plt.gca().set_yticks(np.arange(.5,len(continents),1),minor=True) 
    plt.tick_params(axis='x', which='minor', colors='w')
    plt.tick_params(axis='y', which='minor', colors='w')
    plt.grid(which='minor', color='blue', linestyle=':', linewidth=1)
    plt.text(.94,.90,'from '+continent, size=10, va="center", ha="center", transform=plt.gca().transAxes, rotation=-30, color='white',bbox=dict(boxstyle="Round", alpha=0.7))
    plt.annotate('created on '+dt_string, (0,0), (0, -20), xycoords='axes fraction', textcoords='offset points', va='top', size=8, style='italic')
    saveplt(plt,file_output+'_'+continent)
    plt.clf()


logger.info("End")
