# ***********************************************************************************
# Module that contain classess for providing data to plotting front-end page
# ***********************************************************************************
__author__ = "IU1BOW - Corrado"
import threading
import time
from lib.qry import query_manager
import pandas as pd
import json

# -----------------------------------------------------------------------------------
# Base class (as template for other classes)
# -----------------------------------------------------------------------------------
class BaseDataProvider:

    # glb_data is used for store and return informations to within get_data method
    global glb_data
    global glb_last_refresh
    global glb_response

    # refresh is used to refetch data from db and store in memory. you can define a
    # time for refresh
    def refresh(self):
        self.logger.info("Class: %s refresh data", self.__class__.__name__)
        return {}

    # return data to the caller
    def get_data(self):
        self.glb_response = {}
        self.glb_response.update({"last_refresh": self.glb_last_refresh})
        return self.glb_response

    # constructor: you have to pass logger, continent list and bands (for frequencies)
    # this method call the first refresh
    def __init__(self, logger, qm, continents, bands):
        self.logger = logger
        self.logger.info("Class: %s init start", self.__class__.__name__)
        self.qm = qm
        self.continents = continents
        self.bands = bands
        self.refresh()
        self.logger.info("Class: %s init end", self.__class__.__name__)
        return


# -----------------------------------------------------------------------------------
# Class for managing data for Continent/Band chart
# -----------------------------------------------------------------------------------
class ContinentsBandsProvider(BaseDataProvider):
    def __init__(self, logger, qm, continents, bands):
        # Calling constructor of base class
        super().__init__(logger, qm, continents, bands)

    def __load_data(self, band_frequencies, continents_cq):

        self.logger.info("Start")
        self.logger.info("doing query...")

        # construct bands query
        bands_qry_string = "CASE "
        self.logger.debug(band_frequencies)
        for i in range(len(band_frequencies["bands"])):
            bands_qry_string += (
                " WHEN freq between "
                + str(band_frequencies["bands"][i]["min"])
                + " AND "
                + str(band_frequencies["bands"][i]["max"])
            )
            bands_qry_string += ' THEN "' + band_frequencies["bands"][i]["id"] + '"'

        # construct continent region query
        spottercq_qry_string = "CASE "
        spotcq_qry_string = "CASE "
        for i in range(len(continents_cq["continents"])):
            spottercq_qry_string += (
                " WHEN spottercq in(" + continents_cq["continents"][i]["cq"] + ")"
            )
            spottercq_qry_string += (
                ' THEN "' + continents_cq["continents"][i]["id"] + '"'
            )
            spotcq_qry_string += (
                " WHEN spotcq in(" + continents_cq["continents"][i]["cq"] + ")"
            )
            spotcq_qry_string += ' THEN "' + continents_cq["continents"][i]["id"] + '"'

        # construct final query string
        qry_string = (
            """
			SELECT 
					"""
            + spottercq_qry_string
            + """ ELSE spottercq END,
						"""
            + spotcq_qry_string
            + """ ELSE spotcq END,
						"""
            + bands_qry_string
            + """ END,
						count(0) number
			from spot 
				where
					rowid > (select max(rowid) max_rowid from spot) - 5000 and
					time > UNIX_TIMESTAMP()-3600
				group by 1, 2, 3
				;            
		"""
        )

        self.logger.debug(qry_string)
        self.qm.qry(qry_string)
        data = self.qm.get_data()
        if len(data) == 0:
            self.logger.warning("no data found")

        self.logger.info("query done")
        self.logger.debug(data)

        return data

    # function for search continent in the global data returned by query and making a cartesian product
    # in order to prepare data for heatmap
    def __normalize_continent(self, data_list, continent, continents_list, band_list):
        data_filtered = []
        for i, item_data in enumerate(data_list):
            if item_data[0] == continent and not (item_data[3] is None):
                element = []
                element.append(item_data[1])
                element.append(item_data[2])
                element.append(item_data[3])
                data_filtered.append(element)

        cartesian_product = []

        for j, item_continent in enumerate(continents_list):
            for k, item_band in enumerate(band_list):
                found = 0
                for lis, item_filtered in enumerate(data_filtered):
                    if (
                        item_filtered[0] == item_continent["id"]
                        and item_filtered[1] == item_band["id"]
                    ):
                        # cartesian_product.append(item_filtered)
                        element = []
                        element.append(j)
                        element.append(k)
                        element.append(item_filtered[2])
                        cartesian_product.append(element)
                        found = 1
                if found == 0:
                    element = []
                    element.append(j)
                    element.append(k)
                    element.append(0)
                    cartesian_product.append(element)

        self.logger.debug("cartesian product for continent: " + continent)
        self.logger.debug(cartesian_product)
        return cartesian_product

    def refresh(self):
        super().refresh()
        lcl_data = {}
        qry_data = self.__load_data(self.bands, self.continents)
        for i, item in enumerate(self.continents["continents"]):
            continent = item["id"]
            data_de = self.__normalize_continent(
                qry_data, continent, self.continents["continents"], self.bands["bands"]
            )
            lcl_data.update({continent: data_de})

        self.glb_data = lcl_data
        self.glb_last_refresh = time.time()

        threading.Timer(15 * 60, self.refresh).start()  # periodic refresh: set time
        return

    def get_data(self, continent_filter):
        super().get_data()
        self.glb_response.update({"band activity": self.glb_data[continent_filter]})
        return self.glb_response


# -----------------------------------------------------------------------------------
# Class for managing data for Spots per months chart
# -----------------------------------------------------------------------------------
class SpotsPerMounthProvider(BaseDataProvider):
    def __init__(self, logger, qm):
        # Calling constructor of base class
        super().__init__(logger, qm, [], [])

    def __load_data(self):

        self.logger.info("Start")
        self.logger.info("doing query...")

        # construct final query string
        qry_string = """
		select month(s1.ym) as referring_month, 
			cast(sum(
				case 
					when YEAR(s1.ym)=YEAR(now()) 
					then s1.total 
					else 0
				end
				) as int) as current_year,
			cast(sum(
				case 
					when YEAR(s1.ym)=YEAR(now())-1 
					then s1.total 
					else 0
				end
				) as int) as one_year_ago,
			cast(sum(
				case 
					when YEAR(s1.ym)=YEAR(now())-2 
					then s1.total 
					else 0
				end
				) as int) as two_year_ago		
			from (
				/* extract number of qso per year */
				select 
					CAST(
						CONCAT(
							YEAR(FROM_UNIXTIME(time)),		
							'-',
							right(concat('0',MONTH(FROM_UNIXTIME(time))),2),   
							'-',
							'01'
							)
						AS DATE) as ym,
						count(0) as total
					from spot 
						WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 36 MONTH)
						GROUP by 1
						/*union used to initialize all months */
						union select '1976-01-01', 0        
						union select '1976-02-01', 0         
						union select '1976-03-01', 0       
						union select '1976-04-01', 0
						union select '1976-05-01', 0
						union select '1976-06-01', 0
						union select '1976-07-01', 0
						union select '1976-08-01', 0
						union select '1976-09-01', 0
						union select '1976-10-01', 0
						union select '1976-11-01', 0
						union select '2019-12-01', 0          
			) as s1
			group by referring_month
		;
			"""
        self.logger.debug(qry_string)
        self.qm.qry(qry_string)
        data = self.qm.get_data()
        if len(data) == 0:
            self.logger.warning("no data found")

        self.logger.info("query done")
        self.logger.debug(data)

        return data

    def refresh(self):
        super().refresh()
        lcl_data = {}
        qry_data = self.__load_data()

        for i, item in enumerate(qry_data):
            year_data = {"year_0": item[1], "year_1": item[2], "year_2": item[3]}
            lcl_data.update({item[0]: year_data})

        self.logger.debug(lcl_data)

        self.glb_data = lcl_data
        self.glb_last_refresh = time.time()

        threading.Timer(
            60 * 60 * 24, self.refresh
        ).start()  # periodic refresh: set time
        return

    def get_data(
        self,
    ):
        super().get_data()
        self.glb_response.update({"spots_per_month": self.glb_data})
        return self.glb_response


# -----------------------------------------------------------------------------------
# Class for managing data for Spots trend chart
# -----------------------------------------------------------------------------------
class SpotsTrend(BaseDataProvider):
    def __init__(self, logger, qm):
        # Calling constructor of base class
        super().__init__(logger, qm, [], [])

    def __load_data(self):

        self.logger.info("Start")
        self.logger.info("doing query...")

        # construct final query string
        qry_string = """
		select     
			FROM_UNIXTIME(time,'%Y-%m-%d') as day,                 
			count(0) as total         
			from spot                 
			WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 60 MONTH)                 
			GROUP by 1
		;
		"""
        self.logger.debug(qry_string)
        self.qm.qry_pd(qry_string)
        df = self.qm.get_data()

        self.logger.info("query done")
        self.logger.debug(df)

        if len(df) == 0:
            self.logger.warning("no data found")

        # normalize data eliminating peaks
        df["day"] = pd.to_datetime(df["day"])
        df = df.set_index("day")
        df = df.resample("D").interpolate(
            method="pad", limit_direction="forward", axis=0
        )
        df = df.rolling("30D").mean()
        df["total"] = df["total"].round(0)

        return df

    def refresh(self):
        super().refresh()
        qry_data = self.__load_data()

        lcl_data = {}

        # iterate panda dataframe
        for index, row in qry_data.iterrows():
            lcl_data.update({str(index.date()): row["total"]})

        self.logger.debug(lcl_data)

        self.glb_data = lcl_data
        self.glb_last_refresh = time.time()

        threading.Timer(
            60 * 60 * 24, self.refresh
        ).start()  # periodic refresh: set time
        return

    def get_data(self):
        super().get_data()
        self.glb_response.update({"spots_trend": self.glb_data})
        return self.glb_response


# -----------------------------------------------------------------------------------
# Class for managing data for Hour/Band chart
# -----------------------------------------------------------------------------------
class HourBand(BaseDataProvider):
    def __init__(self, logger, qm, bands):
        # Calling constructor of base class
        super().__init__(logger, qm, [], bands)

    def __load_data(self):

        self.logger.info("Start")
        self.logger.info("doing query...")

        self.logger.debug(self.bands)
        # construct bands query
        bands_qry_string = "CASE "
        for i in range(len(self.bands["bands"])):
            bands_qry_string += (
                " WHEN freq between "
                + str(self.bands["bands"][i]["min"])
                + " AND "
                + str(self.bands["bands"][i]["max"])
            )
            bands_qry_string += ' THEN "' + self.bands["bands"][i]["id"] + '"'

        # construct bands query weight
        bands_weight_qry_string = "CASE "
        for i in range(len(self.bands["bands"])):
            bands_weight_qry_string += (
                " WHEN freq between "
                + str(self.bands["bands"][i]["min"])
                + " AND "
                + str(self.bands["bands"][i]["max"])
            )
            bands_weight_qry_string += (
                ' THEN "' + str(self.bands["bands"][i]["min"]) + '"'
            )

        # construct final query string
        qry_string = (
            """
		select s1.band, s1.hour, s1.total from (
			SELECT 
					cast(concat(HOUR (FROM_UNIXTIME(time))) as unsigned) as hour,
					"""
            + bands_qry_string
            + """ ELSE "other" END as band,
					cast("""
            + bands_weight_qry_string
            + """ ELSE 0 END as unsigned) as band_weight,
					count(0) AS total
			from spot 
					WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 1 MONTH)
					and rowid > (select max(rowid)-500000 from spot) 
				group by 1, 2
				) as s1
				order by s1.band, s1.hour
			; 
		"""
        )

        self.logger.debug(qry_string)
        self.qm.qry(qry_string)
        data = self.qm.get_data()
        if len(data) == 0:
            self.logger.warning("no data found")

        self.logger.info("query done")
        self.logger.debug(data)

        return data

    def refresh(self):
        super().refresh()
        lcl_data = {}
        qry_data = self.__load_data()

        for i, j, k in qry_data:
            if i not in lcl_data:
                lcl_data[i] = {}
            lcl_data[i].update({j: k})

        self.logger.debug(lcl_data)

        self.glb_data = lcl_data
        self.glb_last_refresh = time.time()

        threading.Timer(
            60 * 60 * 24, self.refresh
        ).start()  # periodic refresh: set time
        return

    def get_data(self):
        super().get_data()
        self.glb_response.update({"hour_band": self.glb_data})
        return self.glb_response


# -----------------------------------------------------------------------------------
# Class for managing data for World DX SPOTS current activity
# -----------------------------------------------------------------------------------
class WorldDxSpotsLive(BaseDataProvider):

    global glb_pfxt

    def __init__(self, logger, qm, pfxt):
        # Calling constructor of base class
        self.glb_pfxt = pfxt
        super().__init__(logger, qm, [], [])

    def __load_data(self):
        self.logger.info("Start")
        self.logger.info("doing query...")

        # construct final query string
        qry_string = """
			select spotcall as dx
			from  spot    
			WHERE FROM_UNIXTIME(time) > DATE_SUB(now(), INTERVAL 1 HOUR)
			and rowid > (select max(rowid)-10000 from spot) 
			group by 1;
		"""

        self.logger.debug(qry_string)
        self.qm.qry(qry_string)
        data = self.qm.get_data()
        row_headers = self.qm.get_headers()
        if len(data) == 0:
            self.logger.warning("no data found")

        self.logger.info("query done")
        self.logger.debug(data)

        # define country table for search info on callsigns
        df = pd.DataFrame(columns=["row_id", "dx", "lat", "lon"])
        dx = []
        lat = []
        lon = []
        row_id = []
        idx = 0

        for result in data:
            main_result = dict(zip(row_headers, result))
            # find the country in prefix table
            search_prefix = self.glb_pfxt.find(main_result["dx"])
            if search_prefix["country"] != "unknown country":
                # merge recordset and contry prefix
                dx.append(main_result["dx"])
                lon.append(float(search_prefix["lat"]))
                lat.append(-float(search_prefix["lon"]))
                idx += 1
                row_id.append(idx)

        df["dx"] = dx
        df["lat"] = lat
        df["lon"] = lon
        df["row_id"] = row_id
        df_grp = df.groupby(["lat", "lon"])["row_id"].count().reset_index(name="count")

        if df is None == 0:
            logger.warning("no data found")

        return df_grp

    def refresh(self):
        super().refresh()
        lcl_data = {}
        qry_data = self.__load_data()

        self.logger.debug(qry_data)

        lcl_data = []
        for index, row in qry_data.iterrows():
            record = dict(lat=row["lat"], lon=row["lon"], count=row["count"])
            lcl_data.append(record)

        self.logger.debug(lcl_data)

        self.glb_data = lcl_data
        self.glb_last_refresh = time.time()

        threading.Timer(5 * 60, self.refresh).start()  # periodic refresh: set time
        return

    def get_data(self):
        super().get_data()

        self.glb_response.update({"world_dx_spots_live": self.glb_data})

        return self.glb_response
