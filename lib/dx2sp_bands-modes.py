__author__ = "S50U - Danilo / IU1BOW - Corrado"
"""
This script converts amateur radio band and mode data from the Dxspider format
to the JSON format used by Spiderweb. It reads a Dxspider configuration file,
extracts band and mode information, transforms it, and saves it to two JSON files
(bands.json and modes.json). It also creates a backup of existing files before
overwriting and generates a report of the conversion process.
"""
import re
import json
import datetime
from datetime import datetime, timezone
import os
import sys
import logging
import shutil

# --- Constants ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(levelname)s] %(message)s'
ALL_MODE = 'all'
BANDS_OUTPUT_PATH = "../cfg/bands.json"
MODES_OUTPUT_PATH = "../cfg/modes.json"
BACKUP_SUFFIX_FORMAT = "%Y%m%d_%H%M%S"

# --- Mappings ---
# change them in order to maps bands and modes
# from dxspider to spiderweb.
# the output will be sorted with the same sequence.
SPIDERWEB_BAND_MAP = {
    "160m": "160",
    "80m": "80",
    "60m": "60",
    "40m": "40",
    "30m": "30",
    "20m": "20",
    "17m": "17",
    "15m": "15",
    "12m": "12",
    "10m": "10",
    "6m": "6",
    "2m": "VHF",
    "70cm": "UHF",
    "23cm": "UHF",
    "13cm": "SHF",
    "9cm": "SHF",
    "6cm": "SHF",
    "3cm": "SHF",
}

SPIDERWEB_MODE_MAP = {
    "cw": "cw",
    "data": "digi",
    "sstv": "digi",
    "rtty": "digi",
    "ft8": "digi-ft8",
    "ft4": "digi-ft4",
    "ssb": "phone",
    "space": ALL_MODE,
    "sat": ALL_MODE
}


# --- Logging initialization ---
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

def process_mode_frequencies(mode_id: str, frequencies: list[float], modes_data: dict):
    """
    Adds frequency ranges to modes_data for a given mode_id.

    Args:
        mode_id (str): The identifier of the mode.
        frequencies (list[float]): A list of frequency values (min, max pairs).
        modes_data (dict): The dictionary to which frequency ranges will be added.
    """
    for i in range(0, len(frequencies), 2):
        if i + 1 < len(frequencies):
            modes_data.setdefault(mode_id, []).append({
                "min": frequencies[i],
                "max": frequencies[i + 1]
            })

def filter_and_merge_frequencies(frequencies: list[dict]) -> list[dict]:
    """
    Filters and merges overlapping or adjacent frequency ranges.

    Args:
        frequencies (list[dict]): A list of dictionaries, where each dictionary
                                 has 'min' and 'max' keys representing a frequency range.

    Returns:
        list[dict]: A list of merged and sorted frequency ranges.
    """
    if not frequencies:
        return []
    sorted_frequencies = sorted(frequencies, key=lambda x: x['min'])
    merged_frequencies = [sorted_frequencies[0]]
    for current_range in sorted_frequencies[1:]:
        last_merged_range = merged_frequencies[-1]
        if current_range['min'] <= last_merged_range['max']:
            merged_frequencies[-1] = {
                "min": last_merged_range['min'],
                "max": max(last_merged_range['max'], current_range['max'])
            }
        else:
            merged_frequencies.append(current_range)
    return merged_frequencies

def filter_bands(bands_data_raw: dict) -> dict:
    """
    Finds the overall minimum and maximum frequency for each band.

    Args:
        bands_data_raw (dict): A dictionary where keys are band names and values
                                are lists of frequency range tuples.

    Returns:
        dict: A dictionary where keys are band names and values are tuples
              containing the minimum and maximum frequencies.
    """
    logging.info("Filtering bands data.")
    bands_data = {}
    for band_name, ranges in bands_data_raw.items():
        min_freqs = [r[0] for r in ranges]
        max_freqs = [r[1] for r in ranges]
        bands_data[band_name] = (min(min_freqs), max(max_freqs))
    return bands_data

def sort_dictionary_by_guide(guide_dict: dict, dict_to_sort: dict) -> dict:
    """
    Sorts a dictionary based on the key order of another dictionary.

    Args:
        guide_dict (dict): The dictionary whose key order will be used for sorting.
        dict_to_sort (dict): The dictionary to be sorted.

    Returns:
        dict: A new dictionary with the same key-value pairs as dict_to_sort,
              but ordered according to the keys of guide_dict.
    """
    logging.info("Sorting dictionary.")
    sorted_dict = {}
    for dict_id in guide_dict.values():
        if dict_id in dict_to_sort:
            sorted_dict[dict_id] = dict_to_sort[dict_id]
    return sorted_dict

def backup_file(file_path: str) -> str | None:
    """
    Creates a backup copy of the file if it exists.

    Args:
        file_path (str): The path to the file to backup.

    Returns:
        str | None: The path to the backup file if successful, otherwise None.
    """
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime(BACKUP_SUFFIX_FORMAT)
        backup_path = f"{file_path}_{timestamp}.bck"
        try:
            shutil.copy2(file_path, backup_path)
            logging.info(f"Existing file backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Error creating backup of '{file_path}': {e}")
            return None
    return None

def save_json_data(data: dict, output_path: str):
    """
    Saves a Python dictionary to a JSON file, creating a backup first.

    Args:
        data (dict): The dictionary to save.
        output_path (str): The path to the JSON file where the data will be saved.
    """
    logging.info(f"Saving data to JSON file: {output_path}")
    backup_file(output_path)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logging.info(f"Successfully saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error saving JSON file '{output_path}': {e}")
        raise

def process_dxspider_bands_file(bands_pl_path: str) -> tuple[dict, dict, list[str], list[str]]:
    """
    Processes the Dxspider bands.pl file, extracting band and mode information.

    Args:
        bands_pl_path (str): The full path to the Dxspider bands.pl file.

    Returns:
        tuple[dict, dict, list[str], list[str]]: A tuple containing:
            - bands_data_raw (dict): Raw band data extracted from the file.
            - modes_data_raw (dict): Raw mode data with frequency ranges.
            - not_converted_bands (list[str]): List of bands not converted.
            - not_converted_modes (list[str]): List of modes not converted.
    """
    bands_data_raw = {}
    modes_data_raw = {}
    not_converted_bands = []
    not_converted_modes = []

    logging.info(f"Processing Dxspider bands file: {bands_pl_path}")
    with open(bands_pl_path, "r", encoding="utf-8") as f:
        content = f.read()

    band_entries = re.findall(r"'([^']+)'\s*=>\s*bless\s*\(\s*\{(.*?)\}\s*,\s*'Bands'\s*\)", content, re.DOTALL)

    for dxspider_band_name, band_content in band_entries:
        try:
            spiderweb_band = SPIDERWEB_BAND_MAP[dxspider_band_name]
            logging.debug(f"Mapping band '{dxspider_band_name}' to '{spiderweb_band}'")
            modes = re.findall(r"(\w+)\s*=>\s*\[(.*?)\]", band_content, re.DOTALL)
            band_min = None
            band_max = None
            for dxspider_mode_name, freqs_raw in modes:
                frequencies = [float(f.strip()) for f in freqs_raw.split(",") if f.strip()]
                mode_lower = dxspider_mode_name.lower()
                if mode_lower == 'band':
                    if frequencies:
                        band_min = min(frequencies)
                        band_max = max(frequencies)
                else:
                    try:
                        spiderweb_mode = SPIDERWEB_MODE_MAP[mode_lower]
                        logging.debug(f"Mapping mode '{mode_lower}' to '{spiderweb_mode}'")
                        if spiderweb_mode == ALL_MODE:
                            for mode_id in set(SPIDERWEB_MODE_MAP.values()) - {ALL_MODE}:
                                process_mode_frequencies(mode_id, frequencies, modes_data_raw)
                        else:
                            process_mode_frequencies(spiderweb_mode, frequencies, modes_data_raw)
                    except KeyError:
                        logging.debug(f"Mode '{mode_lower}' not converted.")
                        if mode_lower not in not_converted_modes:
                            not_converted_modes.append(mode_lower)

            if band_min is not None and band_max is not None:
                bands_data_raw.setdefault(spiderweb_band, []).append((band_min, band_max))

        except KeyError:
            logging.debug(f"Band '{dxspider_band_name}' not converted.")
            if dxspider_band_name not in not_converted_bands:
                not_converted_bands.append(dxspider_band_name)

    return bands_data_raw, modes_data_raw, not_converted_bands, not_converted_modes

def create_report(bands_data: dict, modes_data_raw: dict, not_converted_bands: list[str], not_converted_modes: list[str]) -> dict:
    """
    Creates a report on the outcome of the conversion.

    Args:
        bands_data (dict): The processed band data.
        modes_data_raw (dict): The raw processed mode data.
        not_converted_bands (list[str]): List of bands that were not converted.
        not_converted_modes (list[str]): List of modes that were not converted.

    Returns:
        dict: A dictionary containing the conversion report.
    """
    logging.info("Creating conversion report.")
    band_ranges = {band_id: (band_min, band_max) for band_id, (band_min, band_max) in bands_data.items()}
    mode_coverage = {}

    for mode_id, freq_list in modes_data_raw.items():
        for freq_range in freq_list:
            for band_id, (band_min, band_max) in band_ranges.items():
                if freq_range['min'] >= band_min and freq_range['max'] <= band_max:
                    mode_coverage.setdefault(band_id, set()).add(mode_id)

    bands_without_modes = [band_id for band_id in bands_data if band_id not in mode_coverage]
    all_modes_used = set()
    for modes in mode_coverage.values():
        all_modes_used.update(modes)
    modes_without_band = [mode_id for mode_id in modes_data_raw if mode_id not in all_modes_used]

    report = {
        "total_output_bands": len(bands_data),
        "total_output_modes": len(modes_data_raw),
        "not_converted_bands": not_converted_bands,
        "not_converted_modes": not_converted_modes,
        "bands_without_modes": bands_without_modes,
        "modes_without_band": modes_without_band
    }
    return report

def main():
    yellow = '\033[33m'
    red_bold = '\033[1;91m'
    reset = '\033[0m'
    bold = '\033[1m'

    print(f"{yellow}")
    print(f"═══════════════════════════════════════════════════════════════")
    print(f"           ✨ DISCLAIMER: PLEASE READ CAREFULLY! ✨")
    print(f"═══════════════════════════════════════════════════════════════")
    print(f"Please use this script {bold}{yellow}at your own risk{reset}{yellow}. The author is not \nresponsible for any data loss, system damage, or other issues \nthat may arise from its use.{reset}\n")
    print(f"{bold}Description: {reset}")
    print(f"This script converts amateur radio band and mode data from the format used by Dxspider to the JSON format required by Spiderweb. It diligently reads a Dxspider configuration file, carefully extracts the band and mode information, transforms it into a well-structured format, and then saves it into two distinct JSON files. For your peace of mind, the script first {bold}creates a backup copy{reset} of your existing files before proceeding to overwrite them. Finally, it generates a comprehensive report summarizing the outcome of this conversion process.\n")

    print(f"{red_bold}{bold}🚨 WARNING: THIS IS A CRITICAL OPERATION! 🚨{reset}")
    print(f"{red_bold}This operation will {bold}PERMANENTLY REPLACE{reset}{red_bold} your {bold}{BANDS_OUTPUT_PATH.split('/')[-1]} and {bold}{MODES_OUTPUT_PATH.split('/')[-1]} files.{reset}\n")

    while True:
        file_path = input(f"Enter the Dxspinder band.pl full path, (e.g. /home/sysop/spider/data/bands.pl) or type '{bold}exit{reset}' to quit: ")
        bands_pl_path = os.path.expanduser(file_path.strip())
        if bands_pl_path.lower() == 'exit':
            print("Exiting the operation.\n")
            sys.exit()
        elif os.path.exists(bands_pl_path):
            print()
            break
        else:
            print(f"The file '{bands_pl_path}' does not exist. Please enter a valid path.\n")

    bands_data_raw, modes_data_raw, not_converted_bands, not_converted_modes = process_dxspider_bands_file(bands_pl_path)

    # Prepare BANDS JSON structures
    bands_filtered = filter_bands(bands_data_raw)
    bands_data = sort_dictionary_by_guide(SPIDERWEB_BAND_MAP, bands_filtered)

    comments = {
        "creation_date": datetime.now(timezone.utc).isoformat(),
        "script used": os.path.basename(__file__),
        "input_file": bands_pl_path,
    }

    logging.info("Creating bands JSON.")
    bands_json = {
        "_comments": comments,
        "bands": [
            {"id": band_id, "min": band_range[0], "max": band_range[1]}
            for band_id, band_range in bands_data.items()
        ]
    }

    # Prepare MODES JSON structures
    logging.info("Filtering and merging modes frequencies.")
    modes_filtered = {
        mode_id: filter_and_merge_frequencies(freqs)
        for mode_id, freqs in modes_data_raw.items()
    }
    modes_data = sort_dictionary_by_guide(SPIDERWEB_MODE_MAP, modes_filtered)

    logging.info("Creating modes JSON.")
    modes_json = {
        "_comments": comments,
        "modes": [
            {"id": mode_id, "freq": freqs}
            for mode_id, freqs in modes_data.items()
        ]
    }

    # Save JSON files
    save_json_data(bands_json, BANDS_OUTPUT_PATH)
    save_json_data(modes_json, MODES_OUTPUT_PATH)

    # Create and display report
    report = create_report(bands_data,modes_data_raw, not_converted_bands, not_converted_modes)
    print("\n==== REPORT ====")
    print(json.dumps(report, indent=2))
    print("================")

    while True:
        save_report = input("Do you want to save the report to a file? (y/n): ")
        if save_report.lower() == 'y':
            report_filename = input("Enter the name of the report file (e.g., report.json): ")
            try:
                with open(report_filename, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                print(f"Report saved to {report_filename}")
                break  # Exit the loop after successful save
            except Exception as e:
                logging.error(f"Error saving report: {e}")
                print("An error occurred while saving the report. Please try again.")
        elif save_report.lower() == 'n':
            print("Report not saved.")
            break  # Exit the loop if the user chooses not to save
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()