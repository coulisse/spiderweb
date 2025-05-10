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

url = "https://www.country-files.com/cty/cty_wt_mod.dat"
TIMING = 3600 * 24

class prefix_table:
    """
    Class to manage the cty.dat file and search for callsign prefixes.
    """

    def __init__(self, cty_local, country_file):
        """
        Initializes the class.

        - Downloads the cty.dat file.
        - Parses the file and creates the prefix_master dictionary with all prefixes and attributes.
        """
        self.cty_local = cty_local
        self.country_file = country_file
        self.prefix_master = {}
        self.initialization()

    def initialization(self):
        """
        Performs initialization, downloading and parsing data, and sets the update timer.
        """
        self.refresh()
        self.timer = Timer(TIMING, self.initialization)
        self.timer.start()

    def refresh(self):
        """
        Updates the cty.dat file data.
        """
        logging.info("CTY: start initialization")
        if self.get_cty(url, self.cty_local) > 0:
            logging.error("there is a problem during downloading country files!")
            logging.info("continue with previous file")
            logging.info(
                "check the connectivity, or put manually the file " + self.cty_local
            )
        line_num = 0
        line_num_valid = 0
        entities_number = 0
        data = ""
        table = []
        self.prefix_master.clear()
        try:
            with open(self.cty_local, "r") as f:
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
                    # if the row is correct put the row in a master prefix dictionary
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
                    self.prefix_master[row[7].upper()] = single_prefix
                    # managing sub-prefixies
                    sub_prefixies = row[8].split(",")
                    for sb in sub_prefixies:
                        values = {}
                        callsign, values = self.parse_alias(sb, single_prefix)
                        self.prefix_master[callsign] = values

            logging.info("number of entities: " + str(entities_number))
            logging.info("number of single alias: " + str(len(self.prefix_master)))
            self.add_country(self.prefix_master)
            logging.info(
                "memory used for prefix: " + str(self.prefix_master.__sizeof__()) + " bytes"
            )
            logging.info("CTY: initialization complete")
            return

        except Exception as e1:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e1).__name__, e1.args)
            logging.error(message)
            return

    def find(self, callsign):
        """
        Finds information related to a callsign.

        Args:
            callsign: The callsign to search for.

        Returns:
            A dictionary with callsign information,
            or a dictionary with "unknown country" and "xx" if not found.
        """
        try:
            data = dict()
            i = len(callsign)
            callsign = callsign.strip().upper()
            while i > 0:
                try:
                    data = self.prefix_master[callsign[:i]]
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
        """
        Class destructor. Cancels the timer.
        """
        self.timer.cancel()
        logging.info("prefix_table destroyed")

    def download_cty(self, url, cty_local):
        """
        Downloads the cty.dat file from a URL.

        Args:
            url: The URL to download the file from.
            cty_local: The local path to save the file.

        Returns:
            0 on success, 1 on error.
        """
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

    def file_age_in_days(self, pathname):
        """
        Calculates the age of a file in days.

        Args:
            pathname: The path of the file.

        Returns:
            The age of the file in days.
        """
       # return (time.time() - os.stat(pathname).st_ctime) / (24 * 3600)
        return (time.time() - os.stat(pathname).st_ctime) / (TIMING)

    def get_cty(self, url, local):
        """
        Manages the cty.dat file, downloading it if it doesn't exist or is too old.

        Args:
          url: URL of the cty.dat file
          local: Local path of the file
        Returns:
            0 on success, 1 on error
        """
        if os.path.isfile(local):
            age = self.file_age_in_days(local)
            if age > 7:
                logging.info(
                    self.cty_local
                    + " too old ("
                    + str(round(age, 0))
                    + " days): proceding to download it"
                )
                return self.download_cty(url, local)
            logging.info(
                self.cty_local
                + " updated ("
                + str(round(age, 0))
                + " days), is not necessary to download it"
            )
            return 0

        logging.info(self.cty_local + " not present: proceding to download it")
        return self.download_cty(url, local)

    def parse_alias(self, alias, master):
        """
        Parses a prefix alias and gets the exceptions.

        Args:
            alias: The alias string to parse.
            master: The main prefix dictionary.

        Returns:
            A tuple containing the callsign and a dictionary with overrides,
            or -1 on error.
        """
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

    def load_country(self):
        """
        Loads country data from a JSON file.

        Returns:
            A dictionary containing the country data.
        """
        logging.info("loading:" + self.country_file)
        with open(self.country_file) as json_country:
            return json.load(json_country)

    def add_country(self, table):
        """
        Adds country information (ISO, WPX) to the prefix table.

        Args:
            table: The prefix table dictionary to modify.
        """
        country_data = self.load_country()
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