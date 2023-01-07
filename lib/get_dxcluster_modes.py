# *************************************************************************************
# Module used to convert dxcluster band file to band configuration file modes for
# spiderweb
# you can use it in build step
# *************************************************************************************
__author__ = "IU1BOW - Corrado"
import logging
import os
import time
from datetime import datetime
import json
import re
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S",
)
# dxspider_band='/home/sysop/spider/data/bands.pl'
output_modes = "../cfg/modes.json"
# -------------------------------------------------------------------------------------
# reads bands file and convert to json
# -------------------------------------------------------------------------------------
def parse(input_file):
    line_num = 0
    line_num_valid = 0
    data = ""
    band_trigger = False
    try:
        with open(input_file, "r") as f:
            for line in f:
                line_num += 1
                li = line.strip()
                # remove comments
                if li.startswith("%bands = "):
                    band_trigger = True
                if li.endswith(");"):
                    band_trigger = False
                if not li.startswith("#") and band_trigger == True:
                    line_num_valid += 1
                    data += li
        logging.debug("first step parsing output: ")
        logging.debug(data)

        # replacing strings in order to obtain a json
        data = data.lower()
        data = data.replace(" ", "")
        data = data.replace("bless", "")
        data = data.replace("%bands=", "")
        data = data.replace(",'bands'", "")
        data = re.sub(
            r"([\"'])(?:(?=(\\?))\2.)*?\1=>", "", data
        )  # remove token like    '136khz' =>
        data = data.replace("=>", ":")
        data = data.replace("(", "")
        data = data.replace(")", "")
        data = re.sub(r"([a-zA-Z]+):", r'"\1":', data)  # add quotation around words
        data = data.replace(",}", "}")
        data = "[" + data + "]"
        data = data.replace(",]", "]")
        logging.debug("second step parsing output: ")
        logging.debug(data)

        return json.loads(data)

    except Exception as e1:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e1).__name__, e1.args)
        logging.error(message)
        logging.error(input_file)
        return ""


# -------------------------------------------------------------------------------------
# add min max freq element to the related mode in final json
# -------------------------------------------------------------------------------------
def add_freq(mode, freq, json_modes):
    try:
        for modes in json_modes["modes"]:
            if modes["id"] == mode:
                ind_freq = 0
                while ind_freq < len(freq):
                    modes["freq"].append(
                        {"min": freq[ind_freq], "max": freq[ind_freq + 1]}
                    )
                    ind_freq += 2

        return json_modes

    except Exception as e1:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e1).__name__, e1.args)
        logging.error(message)
        return {}


# -------------------------------------------------------------------------------------
# reads bands file and convert to json
# -------------------------------------------------------------------------------------
def create_output(data):

    json_modes = json.loads(
        '{"modes":[{"id":"cw","freq":[]},{"id":"phone","freq":[]},{"id":"digi","freq":[]}]}'
    )

    try:
        for element in data:
            for mode in element:
                if mode == "band":
                    pass
                elif mode == "cw":
                    json_modes = add_freq("cw", element[mode], json_modes)
                elif mode == "ssb":
                    json_modes = add_freq("phone", element[mode], json_modes)
                else:
                    json_modes = add_freq("digi", element[mode], json_modes)

        logging.debug("final step output: ")
        logging.debug(json.dumps(json_modes))
        return json_modes

    except Exception as e1:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e1).__name__, e1.args)
        logging.error(message)
        logging.error(input_file)
        return {}


# *************************************************************************************
# Main
# *************************************************************************************
logging.info("RDxSpider band file conversion starting...")
if len(sys.argv) != 2:
    logging.error("argument invalid. Specify dxcluster band file")
    logging.error("use: python get_dxcluster_modes.py input_file")
    raise Exception()

dxspider_band = sys.argv[1]

parsed = parse(dxspider_band)
if parsed != "":
    json_output = create_output(parsed)
    with open(output_modes, "w") as outfile:
        json.dump(json_output, outfile, indent=4)
    logging.info("modes saved to: " + output_modes)
    logging.info("DxSpider band file conversion completed")
else:
    logging.error("error on parsing input file")
