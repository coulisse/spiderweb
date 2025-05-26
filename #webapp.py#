__author__ = "IU1BOW - Corrado"
import flask
from flask import request, render_template
from flask_wtf.csrf import CSRFProtect
from flask_minify import minify
import datetime
import secrets
import json
import threading
import logging
import logging.config
import asyncio
import requests
import xmltodict
import os
from lib.dxtelnet import fetch_who_and_version
from lib.adxo import get_adxo_events
from lib.qry import query_manager
from lib.cty import prefix_table
from lib.plot_data_provider import ContinentsBandsProvider, SpotsPerMounthProvider, SpotsTrend, HourBand, WorldDxSpotsLive
from lib.qry_builder import query_build, query_build_callsign, query_build_callsing_list
from lib.bandplan import BandPlan
from lib.util import copytree

TIMER_VISIT = 1000
TIMER_ADXO = 12 * 3600
TIMER_WHO = 7 * 60

LOCAL = 'local'
LOCAL_CFG = LOCAL+'/cfg'
LOCAL_DATA = LOCAL+'/data'
LOCAL_LOG = LOCAL+'/log'

def check_create_path(path):
    if not os.path.exists(path):
        print(f"path %s not found",path)
        try:
            os.makedirs(path)
        except Exception as e:
            print("Error creating path")
            print(e)
            raise
        finally:
            return 1
    else:
        return 0
    
if check_create_path(LOCAL_CFG) == 1:
    copytree('cfg',LOCAL_CFG)

check_create_path(LOCAL_LOG)

logging.config.fileConfig(LOCAL_CFG+"/webapp_log_config.ini", disable_existing_loggers=True)
logger = logging.getLogger(__name__)
logger.info("Starting SPIDERWEB")

check_create_path(LOCAL_DATA)

app = flask.Flask(__name__)

app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE="Strict",
)

try:
    version_file = open("static/version.txt", "r")
    app.config["VERSION"] = version_file.read().strip()
    version_file.close    
except Exception as e:
    logger.error("Error reading version file")

logger.info("Version: "+app.config["VERSION"] )

inline_script_nonce = ""

csrf = CSRFProtect(app)

logger.debug(app.config)

if app.config["DEBUG"]:
    minify(app=app, html=False, js=False, cssless=False)
else:
    minify(app=app, html=True, js=True, cssless=False)

#removing whitespace from jinja2 html rendered
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True    

 # load config file
try:
    with open(LOCAL_CFG+"/config.json") as json_data_file:
        cfg = json.load(json_data_file)
except FileNotFoundError as e:
    logger.error("config.json not found in: "+LOCAL_CFG)
    exit(1)

logger.debug("CFG:")
logger.debug(cfg)
# load bands file
with open(LOCAL_CFG+"/bands.json") as json_bands:
    band_frequencies = json.load(json_bands)

# load mode file
with open(LOCAL_CFG+"/modes.json") as json_modes:
    modes_frequencies = json.load(json_modes)

# creating bandplan
bandplan_file = 'static/bandplan.svg'

try:
    bp=BandPlan(logger,band_frequencies, modes_frequencies, 'static/images/icons/icon-512x512-transparent.png')
    bp.create(bandplan_file)
    del bp
except Exception as e:
    logger.error("Bandplan not created")
    logger.error(e)

# load continents-cq file
with open(LOCAL_CFG+"/continents.json") as json_continents:
    continents_cq = json.load(json_continents)

#load visitour counter
visits_file_path = LOCAL_DATA+"/visits.json"
try:
    # Load the visits data from the file
    with open(visits_file_path) as json_visitors:
        visits = json.load(json_visitors)
except FileNotFoundError:
    # If the file does not exist, create an empty visits dictionary
    visits = {}

except json.decoder.JSONDecodeError:
    # If the file is not a valid json file
    logger.warning("No valid data in visit json")
    logger.warning("reset and creation of a new:" + visits_file_path )
    visits = {}

#save visits
def save_visits():
    with open(visits_file_path, "w") as json_file:
        json.dump(visits, json_file)
    logger.info('visit saved on: '+ visits_file_path)

# saving scheduled
def schedule_save():
    save_visits()
    threading.Timer(TIMER_VISIT, schedule_save).start()

# Start scheduling
schedule_save()

# read and set default for enabling cq filter
if cfg.get("enable_cq_filter"):
    enable_cq_filter = cfg["enable_cq_filter"].upper()
else:
    enable_cq_filter = "N"

# define country table for search info on callsigns
pfxt = prefix_table(LOCAL_DATA+"/cty_wt_mod.dat", LOCAL_CFG + "/country.json")  

# create object query manager
qm = query_manager()

# the main query to show spots
# it gets url parameter in order to apply the build the right query
# and apply the filter required. It returns a json with the spots
def spotquery(parameters):
    try:

        if 'callsign' in parameters:
            logger.debug('search callsign')
            query_string = query_build_callsign(logger,parameters['callsign'] )
        else:
            logger.debug('search eith other filters')
            query_string = query_build(logger,parameters,band_frequencies,modes_frequencies,continents_cq,enable_cq_filter)
        qm.qry(query_string)
        data = qm.get_data()
        row_headers = qm.get_headers()

        logger.debug("query done")
        logger.debug(data)

        if data is None or len(data) == 0:
            logger.warning("no data found")

        payload = []
        for result in data:
            # create dictionary from recorset
            main_result = dict(zip(row_headers, result))
            # find the country in prefix table
            search_prefix = pfxt.find(main_result["dx"])
            # merge recordset and contry prefix
            main_result["country"] = search_prefix["country"]
            main_result["iso"] = search_prefix["iso"]

            payload.append({**main_result})

        return payload
    except Exception as e:
        logger.error(e)

# find adxo events
adxo_events = None

def get_adxo():
    global adxo_events
    adxo_events = get_adxo_events()
    threading.Timer(TIMER_ADXO, get_adxo).start()
get_adxo()

# create data provider for charts
heatmap_cbp = ContinentsBandsProvider(logger, qm, continents_cq, band_frequencies)
bar_graph_spm = SpotsPerMounthProvider(logger, qm)
line_graph_st = SpotsTrend(logger, qm)
bubble_graph_hb = HourBand(logger, qm, band_frequencies)
geo_graph_wdsl = WorldDxSpotsLive(logger, qm, pfxt)

# Find who is connected to the cluster with DXSpider version (using a scheduled telnet connection)
whoj = {"data": [], "version": "Unknown", "last_updated": "No data"}

async def _fetch_who_and_version_with_timeout(host, port, user, password, timeout=5):
    try:
        return await asyncio.wait_for(fetch_who_and_version(host, port, user, password), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Timeout of {timeout} seconds reached during the connection to {host}:{port}")
        return None, None
    except Exception as e:
        logger.error(f"Error in fetch with timeout: {e}")
        return None, None

def who_is_connected():
    global whoj
    host = cfg["telnet"]["telnet_host"]
    port = cfg["telnet"]["telnet_port"]
    user = cfg["telnet"]["telnet_user"]
    password = cfg["telnet"]["telnet_password"]
    timeout_seconds = 10  # Imposta il timeout desiderato

    logger.info(f"Refreshing WHO list and DXSpider version from: {host}:{port} with timeout {timeout_seconds} seconds")

    try:
        parsed_data, dxspider_version = asyncio.run(
            _fetch_who_and_version_with_timeout(host, port, user, password, timeout_seconds)
        )

        if parsed_data:
            whoj["data"] = [entry for entry in parsed_data if entry.get("callsign") != user]
        else:
            logger.warning("WHO response was empty or timed out.")
            whoj["data"] = []

        if dxspider_version and dxspider_version != "Unknown":
            whoj["version"] = dxspider_version
        else:
            logger.warning("DXSpider version not found or timed out.")
            whoj["version"] = "Unknown"

        whoj["last_updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%d-%b-%Y %H:%MZ")

        logger.debug(f"WHO data: {whoj['data']}")
        logger.debug(f"DXSpider version: {whoj['version']}")
        logger.debug(f"Last updated: {whoj['last_updated']}")

    except Exception as e:
        logger.error(f"Error connecting to host {host}:{port} - {e}")
        whoj["data"] = []
        whoj["version"] = "Error fetching version"
        whoj["last_updated"] = "Connection error"

    finally:
        threading.Timer(TIMER_WHO, who_is_connected).start()
        logger.debug(f"Final WHO data: {whoj}")

# Call function once at startup
who_is_connected()

#Calculate nonce token used in inline script and in csp "script-src" header
def get_nonce():
    global inline_script_nonce
    inline_script_nonce = secrets.token_hex()
    return inline_script_nonce

#check if it is a unique visitor
def visitor_count():
#   user_ip =request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR')or request.environ.get('HTTP_X_REAL_IP') or request.remote_addr
    if user_ip not in visits:
        visits[user_ip] = 1
    else:
        visits[user_ip] += 1

# ROUTINGS
@app.route("/spotlist", methods=["POST"])
@csrf.exempt
def spotlist():
    logger.debug(request.json)
    response = flask.Response(json.dumps(spotquery(request.json)))
    return response
   
@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def spots():
    
    visitor_count()

    response = flask.Response(
        render_template(
            "index.html",
            inline_script_nonce=get_nonce(),
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["telnet_host"]+":"+cfg["telnet"]["telnet_port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),            
            enable_cq_filter=enable_cq_filter,
            timer_interval=cfg["timer"]["interval"],
            adxo_events=adxo_events,
            continents=continents_cq,
            bands=band_frequencies,
            dx_calls=get_dx_calls(),
        )
    )
    return response

#Show all dx spot callsigns 
def get_dx_calls():
    
    try:
        query_string = query_build_callsing_list()
        qm.qry(query_string)
        data = qm.get_data()
        row_headers = qm.get_headers()

        payload = []
        for result in data:
            main_result = dict(zip(row_headers, result))
            payload.append(main_result["dx"])
        logger.debug("last DX Callsigns:")
        logger.debug(payload)
        return payload
    
    except Exception as e:
        return []
    


@app.route("/service-worker.js", methods=["GET"])
def sw():
    return app.send_static_file("pwa/service-worker.js")

@app.route("/offline.html")
def root():
    return app.send_static_file("html/offline.html")

#used for plots
@app.route("/world.json")  
def world_data():
    return app.send_static_file(LOCAL_DATA+"/world.json")

@app.route("/plots.html")
def plots():
    global whoj
    response = flask.Response(
        render_template(
            "plots.html",
            inline_script_nonce=get_nonce(),
            mycallsign=cfg["mycallsign"],
            telnet=f"{cfg['telnet']['telnet_host']}:{cfg['telnet']['telnet_port']}",
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),
            who=whoj.get("data", []),
            last_updated=whoj.get("last_updated", "No data"),
            dxspider_version=whoj.get("version", "Unknown"),
            continents=continents_cq,
            bands=band_frequencies,
        )
    )
    return response

@app.route("/propagation.html")
def propagation():

    #get solar data in XML format and convert to json
    solar_data={}
    url = "https://www.hamqsl.com/solarxml.php"
    try:
        logger.debug("connection to: " + url)
        req = requests.get(url)
        logger.debug(req.content)
        solar_data = xmltodict.parse(req.content)    
        logger.debug(solar_data)

    except Exception as e1:
        logger.error(e1)

    response = flask.Response(
        render_template(
            "propagation.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["telnet_host"]+":"+cfg["telnet"]["telnet_port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),                     
            solar_data=solar_data
        )
    )

    #response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route("/bandplan.html", methods=["GET"])
def bandplan():
    response = flask.Response(
        render_template(
            "bandplan.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["telnet_host"]+":"+cfg["telnet"]["telnet_port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits), 
            bandplan_svg=bandplan_file                    
        )
    )
    return response    

@app.route("/cookies.html", methods=["GET"])
def cookies():
    response = flask.Response(
        render_template(
            "cookies.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["telnet_host"]+":"+cfg["telnet"]["telnet_port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),                     
        )
    )
    return response

@app.route("/privacy.html", methods=["GET"])
def privacy():
    response = flask.Response(
        render_template(
            "privacy.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["telnet_host"]+":"+cfg["telnet"]["telnet_port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),                     
        )
    )
    return response

@app.route("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")


@app.route("/callsign.html", methods=["GET"])
def callsign():

    callsign = request.args.get("c")
    response = flask.Response(
        render_template(
            "callsign.html",
            inline_script_nonce=get_nonce(),              
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["telnet_host"]+":"+cfg["telnet"]["telnet_port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),                     
            timer_interval=cfg["timer"]["interval"],
            callsign=callsign,
            adxo_events=adxo_events,
            continents=continents_cq,
            bands=band_frequencies,
        )
    )
    return response


# API that search a callsign and return all informations about that
@app.route("/callsign", methods=["GET"])
def find_callsign():
    callsign = request.args.get("c")
    response = pfxt.find(callsign)
    if response is None:
        response = flask.Response(status=204)
    return response


@app.route("/plot_get_heatmap_data", methods=["POST"])
@csrf.exempt
def get_heatmap_data():
    continent = request.json['continent']
    logger.debug(request.get_json())
    response = flask.Response(json.dumps(heatmap_cbp.get_data(continent)))
    logger.debug(response)
    if response is None:
        response = flask.Response(status=204)
    return response


@app.route("/plot_get_dx_spots_per_month", methods=["POST"])
@csrf.exempt
def get_dx_spots_per_month():
    response = flask.Response(json.dumps(bar_graph_spm.get_data()))
    logger.debug(response)
    if response is None:
        response = flask.Response(status=204)
    return response


@app.route("/plot_get_dx_spots_trend", methods=["POST"])
@csrf.exempt
def get_dx_spots_trend():
    response = flask.Response(json.dumps(line_graph_st.get_data()))
    logger.debug(response)
    if response is None:
        response = flask.Response(status=204)
    return response


@app.route("/plot_get_hour_band", methods=["POST"])
@csrf.exempt
def get_dx_hour_band():
    response = flask.Response(json.dumps(bubble_graph_hb.get_data()))
    logger.debug(response)
    if response is None:
        response = flask.Response(status=204)
    return response


@app.route("/plot_get_world_dx_spots_live", methods=["POST"])
@csrf.exempt
def get_world_dx_spots_live():
    response = flask.Response(json.dumps(geo_graph_wdsl.get_data()))
    logger.debug(response)
    if response is None:
        response = flask.Response(status=204)
    return response

@app.route("/csp-reports", methods=['POST'])
@csrf.exempt
def csp_reports():
    report_data = request.get_data(as_text=True)
    logger.warning("CSP Report:")
    logger.warning(report_data)
    response=flask.Response(status=204)
    return response

@app.after_request
def add_security_headers(resp):

    resp.headers["Strict-Transport-Security"] = "max-age=1000"
    resp.headers["X-Xss-Protection"] = "1; mode=block"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    #resp.headers["Access-Control-Allow-Origin"]= "sidc.be prop.kc2g.com www.hamqsl.com"
    #resp.headers["Cache-Control"] = "public, no-cache"
    resp.headers["Cache-Control"] = "public, no-cache, must-revalidate, max-age=900"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["ETag"] = app.config["VERSION"]
    #resp.headers["Report-To"] = '{"group":"csp-endpoint", "max_age":10886400, "endpoints":[{"url":"/csp-reports"}]}'    
    resp.headers["Content-Security-Policy"] = "\
    default-src 'self';\
    script-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net 'nonce-"+inline_script_nonce+"';\
    style-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net;\
    object-src 'none';base-uri 'self';\
    connect-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com sidc.be prop.kc2g.com www.hamqsl.com;\
    font-src 'self' cdn.jsdelivr.net;\
    frame-src 'self';\
    frame-ancestors 'none';\
    form-action 'none';\
    img-src 'self' data: cdnjs.cloudflare.com sidc.be prop.kc2g.com ;\
    manifest-src 'self';\
    media-src 'self';\
    worker-src 'self';\
    report-uri /csp-reports;\
    "
    return resp
   
    #report-to csp-endpoint;\
    #script-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net 'nonce-sedfGFG32xs';\
    #script-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net 'nonce-"+inline_script_nonce+"';\
if __name__ == "__main__":
    who_is_connected()
    app.run(host="0.0.0.0")
