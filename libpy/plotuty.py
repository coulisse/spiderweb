#*****************************************************************************************
# module used to save a plot and delete old plots 
#*****************************************************************************************

__author__ = 'IU1BOW - Corrado'

import logging
import logging.config
from datetime import datetime
import glob
import os
import json

logging.config.fileConfig("../cfg/plots_log_config.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def del_with_retention(filename, number,ext):
#list all file with date time and extension
#and delete al file except the last "number" passed by param, and ordered by name 
    logger.info('deleting old files')
    pattern=filename+'_????????-??????.'+ext
    logger.debug('search pattern for delete files: '+pattern)
    files=glob.glob(pattern)
    length = len(files)
    if length>number:
        files_ordered=sorted(files)   
        i = 0
    # Iterating using while loop 
        while i < length - number: 
            try:
                os.remove(files_ordered[i])
                logger.info('deleted file:'+files_ordered[i])
            except Exception as e:
                logger.error(e)
                logger.error('not deleted file:'+files_ordered[i])
            finally:
                i += 1

    return

def saveplt(plt,filename):
    #convert relative to absolute path
    #filename=os.path.abspath(os.path.expanduser(os.path.expandvars(filename)))
    now = datetime.now() # current date and time
    timestamp=now.strftime("%Y%m%d-%H%M%S")
    outputfile=filename+'_'+timestamp

    #saving svg file
    try:
        plt.savefig(outputfile+'.svg', dpi=100, bbox_inches='tight')    
        logger.info('plotted saved on: '+outputfile+'.svg')
    except Exception as e01:
        logger.error(e01)
        logger.error('error saving file: '+outputfile+'.svg')

    #saving png file
    try:
        plt.savefig(outputfile+'.png', dpi=100, bbox_inches='tight')  
        logger.info('plotted saved on: '+outputfile+'.png')    
    except Exception as e02:
        logger.error(e02)
        logger.error('error saving file: '+outputfile+'.png')

    #creating idx file in order to match standard file name to filename with timestamp
    try:
        basepath=os.path.dirname(filename)
        idxfile=os.path.join(basepath,'plots.json')
        if os.path.exists(idxfile):
            logger.debug(idxfile+' found')
            with open(idxfile,'r') as jsonfile:
                json_content = json.load(jsonfile) # this is now in memory! you can use it outside 'open'
        else:
            logger.debug(idxfile+ ' not found')
            json_content={}

        json_content[os.path.basename(filename)] = os.path.basename(outputfile)
        with open(idxfile,'w') as jsonfile:
            json.dump(json_content, jsonfile, indent=4) # you decide the indentation level

        logging.info(idxfile+' updated')

    except Exception as e03:
        logger.error(e03)
        logger.error('error writing idx: '+idxfile)

    del_with_retention(filename,2,'svg')
    del_with_retention(filename,2,'png')
    return
