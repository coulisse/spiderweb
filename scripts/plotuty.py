__author__ = 'IU1BOW - Corrado'

import logging
import logging.config

logging.config.fileConfig("../cfg/log_config.ini", disable_existing_loggers=False)

def saveplt(plt,filename):
    plt.savefig(filename+'.svg', dpi=100, bbox_inches='tight')    
    logging.info("plotted saved on: "+filename+'.svg')
    plt.savefig(filename+'.png', dpi=100, bbox_inches='tight')  
    logging.info("plotted saved on: "+filename+'.png')    


