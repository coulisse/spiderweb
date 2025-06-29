import json

import lib.constants as CONST
from lib.adxo import get_adxo_events
from lib.qry import query_manager
from lib.cty import prefix_table
from lib.plot_data_provider import ContinentsBandsProvider, SpotsPerMounthProvider, SpotsTrend, HourBand, WorldDxSpotsLive
from lib.qry_builder import query_build, query_build_callsign, query_build_callsing_list

class DataManager:
    """Manages various data objects and query functionalities."""
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.band_frequencies = {}
        self.modes_frequencies = {}
        self.continents_cq = {}
        self.pfxt = None
        self.qm = None
        self.heatmap_cbp = None
        self.bar_graph_spm = None
        self.line_graph_st = None
        self.bubble_graph_hb = None
        self.geo_graph_wdsl = None
        self.visits = self._load_visits()
        self.adxo_events = None

        self._init_data_objects()

    def _load_visits(self):
        """Loads visit data from file."""
        try:
            with open(CONST.VISITS_FILE) as json_visitors:
                visits = json.load(json_visitors)
        except FileNotFoundError:
            visits = {}
        except json.decoder.JSONDecodeError:
            self.logger.warning("No valid data in visit JSON. Resetting visits.")
            visits = {}
        return visits

    def save_visits(self):
        """Saves current visit data to file."""
        with open(CONST.VISITS_FILE, "w") as json_file:
            json.dump(self.visits, json_file)
        self.logger.info(f'Visits saved to: {CONST.VISITS_FILE}')

    def _init_data_objects(self):
        """Initializes various data objects and managers."""
        self.logger.info("Initializing data objects...")

        with open(CONST.BANDS) as json_bands:
            self.band_frequencies = json.load(json_bands)

        with open(CONST.MODES) as json_modes:
            self.modes_frequencies = json.load(json_modes)

        with open(CONST.CONTINENTS) as json_continents:
            self.continents_cq = json.load(json_continents)

        self.pfxt = prefix_table(CONST.CTY_DATA, CONST.COUNTRIES)

        if self.qm is not None:
            try:
                self.qm.close()
                self.logger.info("Existing query_manager instance closed.")
            except Exception as e:
                self.logger.warning(f"Failed to gracefully close existing query_manager: {e}")
                del self.qm
        self.qm = query_manager(self.config.cfg)

        self.heatmap_cbp = ContinentsBandsProvider(self.logger, self.qm, self.continents_cq, self.band_frequencies)
        self.bar_graph_spm = SpotsPerMounthProvider(self.logger, self.qm)
        self.line_graph_st = SpotsTrend(self.logger, self.qm)
        self.bubble_graph_hb = HourBand(self.logger, self.qm, self.band_frequencies)
        self.geo_graph_wdsl = WorldDxSpotsLive(self.logger, self.qm, self.pfxt)
        self.logger.info("Data objects initialized.")

    def spotquery(self, parameters):
        """Executes a spot query based on provided parameters."""
        try:
            if 'callsign' in parameters:
                self.logger.debug('Searching by callsign')
                query_string = query_build_callsign(self.logger, parameters['callsign'])
            else:
                self.logger.debug('Searching with other filters')
                query_string = query_build(self.logger, parameters, self.band_frequencies, self.modes_frequencies, self.continents_cq)

            self.qm.qry(query_string)
            data = self.qm.get_data()
            row_headers = self.qm.get_headers()

            if not data:
                self.logger.warning("No data found for the query.")
                return []

            payload = []
            for result in data:
                main_result = dict(zip(row_headers, result))
                search_prefix = self.pfxt.find(main_result["dx"])
                main_result["country"] = search_prefix["country"]
                main_result["iso"] = search_prefix["iso"]
                payload.append(main_result)
            return payload
        except Exception as e:
            self.logger.error(f"Error in spotquery: {e}")
            return []

    def get_dx_calls(self):
        """Retrieves a list of DX callsigns."""
        try:
            query_string = query_build_callsing_list()
            self.qm.qry(query_string)
            data = self.qm.get_data()
            row_headers = self.qm.get_headers()

            payload = [dict(zip(row_headers, result))["dx"] for result in data]
            self.logger.debug("Last DX Callsigns: %s", payload)
            return payload
        except Exception as e:
            self.logger.error(f"Error fetching DX calls: {e}")
            return []

    def get_adxo_events_data(self):
        """Fetches ADXO events."""
        self.adxo_events = get_adxo_events()
        self.logger.info("ADXO events fetched.")
        return self.adxo_events

    def increment_visitor_count(self, request_environ, remote_addr):
        """Increments visitor count based on IP."""
        user_ip = request_environ.get('HTTP_X_FORWARDED_FOR') or request_environ.get('HTTP_X_REAL_IP') or remote_addr
        self.visits[user_ip] = self.visits.get(user_ip, 0) + 1
