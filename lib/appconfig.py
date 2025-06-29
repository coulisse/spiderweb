import json
import lib.constants as CONST

class AppConfig:
    """Manages application configuration loading and saving."""
    def __init__(self, logger):
        self.logger = logger
        self.cfg = self._load_config()

    def _load_config(self):
        """Loads configuration from JSON files."""
        try:
            with open(CONST.CFG_JSON) as json_data_file:
                cfg = json.load(json_data_file)
        except FileNotFoundError:
            self.logger.warning(f"config.json not found in: {CONST.LOCAL_CFG}. Falling back to template.")
            try:
                with open(CONST.CFG_JSON_TEMPLATE) as json_data_file:
                    cfg = json.load(json_data_file)
            except Exception as e:
                self.logger.error(f"Error loading template config: {e}")
                cfg = None
        return cfg

    def save_config(self, new_cfg_data):
        """Saves new configuration data to the config file."""
        try:
            with open(CONST.CFG_JSON, 'w') as f:
                json.dump(new_cfg_data, f, indent=2)
            self.cfg = new_cfg_data  # Update the in-memory config
            self.logger.info("Configuration saved successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
