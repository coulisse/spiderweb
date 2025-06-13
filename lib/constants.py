#timers
TIMER_VISIT = 1000
TIMER_ADXO = 12 * 3600
TIMER_WHO = 7 * 60

#files and path
LOCAL = 'local'
LOCAL_CFG = LOCAL+'/cfg'
LOCAL_DATA = LOCAL+'/data'
LOCAL_LOG = LOCAL+'/log'
CFG_JSON = LOCAL_CFG+"/config.json"
CFG_JSON_TEMPLATE = CFG_JSON+".template"
BANDS = LOCAL_CFG+"/bands.json"
MODES = LOCAL_CFG+"/modes.json"
CONTINENTS = LOCAL_CFG+"/continents.json"
COUNTRIES = LOCAL_CFG+"/country.json"
INI_CONFIG = LOCAL_CFG+"/webapp_log_config.ini"
VISITS_FILE = LOCAL_DATA+"/visits.json"
CTY_DATA = LOCAL_DATA+"/cty_wt_mod.dat"
VERSION_FILE = "static/version.txt"
BANDPLAN = "static/bandplan.svg"


#various
SOLAR_DATA_URL = "https://www.hamqsl.com/solarxml.php"

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'password' # This password MUST be changed

WHO_TIMEOUT = 10 #timeout in seconds
