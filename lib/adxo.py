# ***********************************************************************************
# Module used to get Announced DX Operation from NG3K website via .ICS (Calendar)
# file, parse it and return a dictionary with these events
# ***********************************************************************************
__author__ = "IU1BOW - Corrado"
import requests
import logging
from datetime import datetime
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
)
# format single line
def format_line(prop):
    prop_out = dict()
    try:
        dtstart = datetime.strptime(prop["DTSTART;VALUE=DATE"], "%Y%m%d")
        dtend = datetime.strptime(prop["DTEND;VALUE=DATE"], "%Y%m%d")
        now = datetime.now()
        if dtstart <= now and dtend >= now:
            prop_out["start"] = dtstart.strftime("%Y-%m-%dT%H:%M:%S%z")
            prop_out["end"] = dtend.strftime("%Y-%m-%dT%H:%M:%S%z")
            prop_out["summary"] = prop["SUMMARY"].split("(")[0].strip()
            prop_out["callsign"] = prop["SUMMARY"].split("(", 1)[1].split(")", 1)[0]
            prop_out["description"] = prop["DESCRIPTION"].replace("\\", "")

    except KeyError:
        pass

    return prop_out


# TODO: url from conf parameter


def get_adxo_events():
    url = "http://dxcal.kj4z.com/dxcal"
    line_num = 0
    event_num = 0
    try:
        logging.info("connection to: " + url)
        req = requests.get(url)
        events = []
        prop = dict()
        prop_name = ""
        with tempfile.TemporaryFile() as temp:
            temp.write(req.content)
            temp.seek(0)
            lines = temp.readlines()
            for line_bytes in lines:
                line = line_bytes.decode()
                line_num += 1
                current_line_array = line.strip().split(":", 1)
                if current_line_array[0] == "BEGIN":
                    if current_line_array[1] == "VCALENDAR":
                        prop = {}
                    if current_line_array[1] == "VEVENT":
                        event_num += 1
                        prop = {}
                else:
                    if current_line_array[0] == "END":
                        if current_line_array[1] == "VCALENDAR":
                            pass
                        if current_line_array[1] == "VEVENT":
                            prop = format_line(prop)
                            if prop:
                                events.append(prop)
                    else:
                        if len(current_line_array) > 1:
                            prop_name = current_line_array[0]
                            prop[prop_name] = current_line_array[1]
                        else:
                            if len(prop_name) > 0:
                                prop[prop_name] = (
                                    prop[prop_name] + current_line_array[0]
                                )

        logging.debug("number of line reads: " + str(line_num))
        logging.info("number ADXO events: " + str(event_num))
        return events
    except Exception as e1:
        logging.error(e1)
        return
