# ***********************************************************************************
# Module used to get Announced DX Operation from NG3K website via rss feed
# file, parse it and return a dictionary with these events
# ***********************************************************************************
__author__ = "IU1BOW - Corrado"
import requests
import logging
from datetime import datetime
import requests
import feedparser
import re
import unicodedata

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def get_adxo_events():
    # URL del file XML RSS

    rss_url = "https://www.ng3k.com/adxo.xml"    

    try:

        # download XML
        response = requests.get(rss_url)
        xml_content = response.content

        # parse XML
        feed = feedparser.parse(xml_content)
        events = []
        prop = dict()
        now = datetime.now()

        # extract elements
        for item in feed.entries:
            prop = {}
            title = item.title

            #bash debug command for list how many commas for each title
            #curl https://www.ng3k.com/adxo.xml | grep title | awk -F',' '{print "Row " NR " has " NF-1 " comma: " $0}'      
            
            #if there are two commas replace them with space in order to normalize a string like this:
            #       "Dominica: Dec 26, 2024-Jan 4, 2025 -- J75K -- QSL via: LoTW       "
            #it will be
            #       "Dominica: Dec 26  2024-Jan 4  2025 -- J75K -- QSL via: LoTW       "

            logging.debug('===========================================================')
            logging.debug(title)

            if title.count(',') == 2: 
                title=title.replace(',', ' ')      

            #callsign
            start_callsign_idx = title.find("--")
            end_callsign_idx = title.find("--", start_callsign_idx + 2)
            prop["callsign"] = title[start_callsign_idx + 2:end_callsign_idx].strip()
           
            #period
            period = title[title.find(":")+1: start_callsign_idx] 

            comma_year_idx = period.find(",")
            #start date - end date
            if comma_year_idx > 0:
                #Mar 23-Apr 1, 2024 or Mar 23-30, 2024 
                year = period[comma_year_idx+1:].strip()
                logging.debug("year: {}".format(year))
                date_start = period[:period.find("-")]+" "+year
                logging.debug("date_start: {}".format(date_start))
                date_end = period[period.find("-")+1:comma_year_idx]+" "+year
                logging.debug("date_end: {}".format(date_end))                
                match = re.search(r"^([A-Za-z]{3}) \d{1,2} \d{4}$", date_end)
                if match:
                    #Mar 23-Apr 1, 2024    
                    pass
                else:
                    #Mar 23-30, 2024 
                    date_end=date_start[:5]+date_end                 
                    logging.debug("date_end: {}".format(date_end))                
            else:
                #Mar 23 2023-Apr 1 2024 
                date_start = period[:period.find("-")]
                logging.debug("date_start: {}".format(date_start))
                date_end = period[period.find("-")+1:]
                logging.debug("date_end: {}".format(date_end))          

            try:
                prop["start"] = datetime.strptime(date_start.strip(), "%b %d %Y")
                prop["end"] = datetime.strptime(date_end.strip(), "%b %d %Y")

            except Exception as eDate:
                logging.error("Dates not decoded:")
                logging.error(eDate)
                logging.error("Date start: {}".format(date_start))
                logging.error("Date end: {}".format(date_end))
                #since is not decoded assign current date
                prop["start"]= datetime.now()
                prop["end"]= datetime.now()

            prop["summary"] = remove_control_characters(title)
            prop["description"] = remove_control_characters(item.description)

            logging.debug("date start: "+ str(prop["start"]) )                
            logging.debug("date end: "+ str(prop["end"]) )                   

            #append only valids (in date) events
            if prop["start"] <= now and prop["end"] >= now:
                events.append(prop)
                logging.debug("Event added")
            else:
                logging.debug("Discarted because not in current date range")

        logging.debug(events)
        if len(events) > 0:
            logging.info("number ADXO events: " + str(len(events)))
        else:
            logging.warning("No ADXO events founds")

        return events
    
    except Exception as e1:
        logging.error(e1)
        return
