import threading
import asyncio
import datetime

import lib.constants as CONST
from lib.dxtelnet import fetch_who_and_version

class BackgroundTaskManager:
    """Manages scheduled background tasks."""
    def __init__(self, logger, data_manager, app_config):
        self.logger = logger
        self.data_manager = data_manager
        self.app_config = app_config
        self.whoj = {"data": [], "version": "Unknown", "last_updated": "No data"}
        # Schedule initial runs and then recurring tasks
        self.schedule_save()
        self.get_adxo_scheduled()
        # Initial call to who_is_connected_scheduled needs to be outside threading.Timer for immediate execution
        self.who_is_connected_scheduled()


    def schedule_save(self):
        """Schedules periodic saving of visit data."""
        self.data_manager.save_visits()
        threading.Timer(CONST.TIMER_VISIT, self.schedule_save).start()

    def get_adxo_scheduled(self):
        """Schedules periodic fetching of ADXO events."""
        self.data_manager.get_adxo_events_data()
        threading.Timer(CONST.TIMER_ADXO, self.get_adxo_scheduled).start()

    async def _fetch_who_and_version_with_timeout(self, host, port, user, password, timeout=5):
        """Fetches WHO data with a timeout."""
        try:
            return await asyncio.wait_for(fetch_who_and_version(host, port, user, password), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout of {timeout} seconds reached during connection to {host}:{port}")
            return None, None
        except Exception as e:
            self.logger.error(f"Error in fetch with timeout: {e}")
            return None, None

    def who_is_connected_scheduled(self):
        """Schedules periodic fetching of connected users and DXSpider version."""
        cfg = self.app_config.cfg
        host = cfg["telnet"]["telnet_host"] if cfg else ""
        port = cfg["telnet"]["telnet_port"] if cfg else ""
        user = cfg["telnet"]["telnet_user"] if cfg else ""
        password = cfg["telnet"]["telnet_password"] if cfg else ""

        self.logger.info(f"Refreshing WHO list and DXSpider version from: {host}:{port} with timeout {CONST.WHO_TIMEOUT} seconds")

        try:
            parsed_data, dxspider_version = asyncio.run(
                self._fetch_who_and_version_with_timeout(host, port, user, password, CONST.WHO_TIMEOUT)
            )

            if parsed_data:
                self.whoj["data"] = [entry for entry in parsed_data if entry.get("callsign") != user]
            else:
                self.logger.warning("WHO response was empty or timed out.")
                self.whoj["data"] = []

            if dxspider_version and dxspider_version != "Unknown":
                self.whoj["version"] = dxspider_version
            else:
                self.logger.warning("DXSpider version not found or timed out.")
                self.whoj["version"] = "Unknown"

            self.whoj["last_updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%d-%b-%Y %H:%MZ")

        except Exception as e:
            self.logger.error(f"Error connecting to host {host}:{port} - {e}")
            self.whoj["data"] = []
            self.whoj["version"] = "Error fetching version"
            self.whoj["last_updated"] = "Connection error"
        finally:
            threading.Timer(CONST.TIMER_WHO, self.who_is_connected_scheduled).start()
            self.logger.debug(f"Final WHO data: {self.whoj}")
