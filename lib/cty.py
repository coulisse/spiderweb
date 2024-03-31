# *************************************************************************************
# Module used to download cty.dat country file and search callsign in it
# *************************************************************************************
__author__ = "IU1BOW - Corrado"
import requests
import logging
import os
import time
from threading import Timer
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
)
# TODO: url from conf parameter
url = "https://www.country-files.com/cty/cty_wt_mod.dat"
cty_local = os.path.dirname(__file__) + "/../data/cty_wt_mod.dat"
country_file = os.path.dirname(__file__) + "/../cfg/country.json"
# -------------------------------------------------------------------------------------
#  download country files cty.dat
# -------------------------------------------------------------------------------------
def download_cty(url, cty_local):
    try:
        logging.info("connection to: " + url)
        req = requests.get(url)
        f = open(cty_local, "wb")
        f.write(req.content)
        f.close()
        logging.info("cty file saved in: " + cty_local)
        return 0

    except Exception as e1:
        logging.error(e1)
        return 1


# -------------------------------------------------------------------------------------
# get age of a file in days
# -------------------------------------------------------------------------------------
def file_age_in_days(pathname):
    return (time.time() - os.stat(pathname).st_ctime) / (24 * 3600)


# -------------------------------------------------------------------------------------
#  manage file cty.dat
# -------------------------------------------------------------------------------------
def get_cty(url, local):
    if os.path.isfile(local):
        age = file_age_in_days(local)
        if age > 7:
            logging.info(
                cty_local
                + " too old ("
                + str(round(age, 0))
                + " days): proceding to download it"
            )
            return download_cty(url, local)
        #        else:
        #           logging.info(cty_local+' updated ('+str(round(age,0))+' days), is not necessary to download it')
        #           return 0
        logging.info(
            cty_local
            + " updated ("
            + str(round(age, 0))
            + " days), is not necessary to download it"
        )
        return 0
    # else:
    #     logging.info(cty_local+' not present: proceding to download it')
    #     return download_cty(url,local)

    logging.info(cty_local + " not present: proceding to download it")
    return download_cty(url, local)


# -------------------------------------------------------------------------------------
#  parsing alias and get exceptions
# -------------------------------------------------------------------------------------
def parse_alias(alias, master):

    try:
        # create a dictionary of array, with start and end position of each exception
        find_dict = {}
        find_dict["pos_cq"] = [alias.find("("), alias.find(")")]
        find_dict["pos_itu"] = [alias.find("["), alias.find("]")]
        find_dict["pos_lat_lon"] = [alias.find("<"), alias.find(">")]
        find_dict["pos_continent"] = [alias.find("{"), alias.find("}")]
        find_dict["pos_time"] = [alias.find("~"), alias[: alias.find("~")].find("~")]

        first = 9999
        parsed = {}

        # assign default values from master callsing
        parsed["country"] = master["country"]
        parsed["cq"] = master["cq"]
        parsed["itu"] = master["itu"]
        parsed["continent"] = master["continent"]
        parsed["lat"] = master["lat"]
        parsed["lon"] = master["lon"]
        parsed["time_loc"] = master["time_loc"]
        parsed["full"] = master["full"]
        parsed["darc_waedc"] = master["darc_waedc"]

        # extract override cq
        if find_dict["pos_cq"][0] >= 0:
            parsed["cq"] = alias[find_dict["pos_cq"][0] + 1 : find_dict["pos_cq"][1]]
            if find_dict["pos_cq"][0] < first:
                first = find_dict["pos_cq"][0]

        # extract override itu
        if find_dict["pos_itu"][0] >= 0:
            parsed["itu"] = alias[find_dict["pos_itu"][0] + 1 : find_dict["pos_itu"][1]]
            if find_dict["pos_itu"][0] < first:
                first = find_dict["pos_itu"][0]

        # extract override lat_lon
        if find_dict["pos_lat_lon"][0] >= 0:
            lat_lon = alias[
                find_dict["pos_lat_lon"][0] + 1 : find_dict["pos_lat_lon"][1]
            ]
            parsed["lat"] = lat_lon[0:].split("/")[0]
            parsed["lon"] = lat_lon[: len(lat_lon)].split("/")[1]
            if find_dict["pos_lat_lon"][0] < first:
                first = find_dict["pos_lat_lon"][0]

        # extract override continent
        if find_dict["pos_continent"][0] >= 0:
            parsed["continent"] = alias[
                find_dict["pos_continent"][0] + 1 : find_dict["pos_continent"][1]
            ]
            if find_dict["pos_continent"][0] < first:
                first = find_dict["pos_continent"][0]

        # extract override time
        if find_dict["pos_time"][0] >= 0:
            parsed["time_loc"] = alias[
                find_dict["pos_time"][0] + 1 : find_dict["pos_time"][1]
            ]
            if find_dict["pos_time"][0] < first:
                first = find_dict["pos_time"][0]

        # extract callsign
        callsing = alias[:first].upper()
        if callsing.startswith("="):
            parsed["full"] = "y"
            callsing = callsing[1:]

        if callsing.startswith("*"):
            parsed["darc_waedc"] = "y"
            callsing = callsing[1:]

        return callsing, parsed

    except Exception as e1:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e1).__name__, e1.args)
        logging.error(message)
        logging.error(alias)
        return -1


# -------------------------------------------------------------------------------------
#  load file from configuration, containing all world country, with related ISO codes
# -------------------------------------------------------------------------------------
def load_country():
    logging.info('loading:' +country_file)
    with open(country_file) as json_country:
        return json.load(json_country)


# -------------------------------------------------------------------------------------
#  search for ISO code, transcoding the country description
# -------------------------------------------------------------------------------------
def add_country(table):
    country_data = load_country()
    for key, value in table.items():
        found = 0
        for i in country_data["country_codes"]:
            if i["desc"].upper() == value["country"].upper():
                value["iso"] = i["ISO"]
                value["wpx"] = i["WPX"]
                found = 1
                break
        if found == 0:
            logging.warning(
                'country "' + value["country"] + '" not found in cfg/country.json'
            )
    return


class prefix_table:

    # -------------------------------------------------------------------------------------
    #  init of the class
    #  - download file cty.dat
    #  - parse file and create prefix_master with all prefixies and attributes
    # .....................................................................................
    # CTY.DAT Format
    #
    # reference: https://www.country-files.com/cty-dat-format/
    #
    # Note that the fields are aligned in columns and spaced out for readability only. It
    # is the “:” at the end of each field that acts as a delimiter for that field:
    # Column 	Length 	Description
    # 1 	26 	Country Name
    # 27 	5 	CQ Zone
    # 32 	5 	ITU Zone
    # 37 	5 	2-letter continent abbreviation
    # 42 	9 	Latitude in degrees, + for North
    # 51 	10 	Longitude in degrees, + for West
    # 61 	9 	Local time offset from GMT
    # 70 	6 	Primary DXCC Prefix (A “*” preceding this prefix indicates that the country
    #           is on the DARC WAEDC list, and counts in CQ-sponsored contests, but not
    #           ARRL-sponsored contests).
    #
    # Alias DXCC prefixes (including the primary one) follow on consecutive lines,
    # separated by commas (,). Multiple lines are OK; a line to be continued should end with
    # comma (,) though it’s not required. A semi-colon (;) terminates the last alias
    # prefix in the list.
    #
    # If an alias prefix is preceded by ‘=’, this indicates that the prefix is to be treated
    # as a full callsign, i.e. must be an exact match.
    #
    # The following special characters can be applied after an alias prefix:
    # (#) 	Override CQ Zone
    # [#] 	Override ITU Zone
    # <#/#> 	Override latitude/longitude
    # {aa} 	Override Continent
    # ~#~ 	Override local time offset from GMT
    #
    # -------------------------------------------------------------------------------------
    def __init__(self):

        global prefix_master
        prefix_master = dict()
        initialization()
        return

    global initialization

    def initialization():
        refresh()
        global timer
        timer = Timer(3600 * 24, initialization)  # try to refresh once a day
        timer.start()
        return

    # -------------------------------------------------------------------------------------
    #  refresh data
    # -------------------------------------------------------------------------------------
    global refresh

    def refresh():

        logging.info("CTY: start initialization")
        if get_cty(url, cty_local) > 0:
            logging.error("there is a problem during downloading country files!")
            logging.info("continue with previous file")
            logging.info(
                "check the connectivity, or put manually the file " + cty_local
            )
        line_num = 0
        line_num_valid = 0
        entities_number = 0
        data = ""
        table = []
        prefix_master.clear()
        try:
            with open(cty_local, "r") as f:
                for line in f:
                    line_num += 1
                    li = line.strip()
                    # remove comments
                    if not li.startswith("#"):
                        line_num_valid += 1
                        data += li
            logging.info("number of lines reads: " + str(line_num))
            logging.info("number of valid lines: " + str(line_num_valid))

            # split in array of lines terminated with semicolon
            table = data.split(";")
            for i, item_table in enumerate(table):
                row = item_table.split(":")
                # remove trailing spaces and uppercasing
                row = [x.strip(" ") for x in row]
                if len(row) == 9:
                    # if the row is corret put the row in a master prefix dictionary
                    entities_number += 1
                    single_prefix = {}
                    single_prefix["country"] = row[0]
                    single_prefix["cq"] = row[1]
                    single_prefix["itu"] = row[2]
                    single_prefix["continent"] = row[3]
                    single_prefix["lat"] = row[4]
                    single_prefix["lon"] = row[5]
                    single_prefix["time_loc"] = row[6]
                    single_prefix["full"] = "n"
                    single_prefix["darc_waedc"] = "n"
                    prefix_master[row[7].upper()] = single_prefix
                    # managing sub-prefixies
                    sub_prefixies = row[8].split(",")
                    for sb in sub_prefixies:
                        values = {}
                        callsign, values = parse_alias(sb, single_prefix)
                        prefix_master[callsign] = values

            logging.info("number of entities: " + str(entities_number))
            logging.info("number of single alias: " + str(len(prefix_master)))
            add_country(prefix_master)
            logging.info(
                "memory used for prefix: " + str(prefix_master.__sizeof__()) + " bytes"
            )
            logging.info("CTY: initialization complete")
            return

        except Exception as e1:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e1).__name__, e1.args)
            logging.error(message)
            return

    # -------------------------------------------------------------------------------------
    #  find a  callsign
    # -------------------------------------------------------------------------------------
    def find(self, callsign):

        try:
            data = dict()
            i = len(callsign)
            callsign = callsign.strip().upper()
            while i > 0:
                try:
                    data = prefix_master[callsign[:i]]
                    data["match"] = callsign[:i]
                    return data
                except KeyError:
                    pass
                i -= 1

        except Exception as e1:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e1).__name__, e1.args)
            logging.error(message)
            return data

        # not found
        data["country"] = "unknown country"
        data["iso"] = "xx"
        return data

    def __del__(self):
        timer.cancel()
        logging.info("prefix_table destroyed")
        return
