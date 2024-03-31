__author__ = "IU1BOW - Corrado"
import flask
import secrets
from flask import request, render_template
from flask_wtf.csrf import CSRFProtect
from flask_minify import minify
import json
import threading
import logging
import logging.config
from lib.dxtelnet import who
from lib.adxo import get_adxo_events
from lib.qry import query_manager
from lib.cty import prefix_table
from lib.plot_data_provider import ContinentsBandsProvider, SpotsPerMounthProvider, SpotsTrend, HourBand, WorldDxSpotsLive
import requests
import xmltodict
from lib.qry_builder import query_build, query_build_callsign, query_build_callsing_list


logging.config.fileConfig("cfg/webapp_log_config.ini", disable_existing_loggers=True)
logger = logging.getLogger(__name__)
logger.info("Starting SPIDERWEB")

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE="Strict",
)
version_file = open("cfg/version.txt", "r")
app.config["VERSION"] = version_file.read().strip()
version_file.close
logger.info("Version:"+app.config["VERSION"] )

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
with open("cfg/config.json") as json_data_file:
    cfg = json.load(json_data_file)

logging.debug("CFG:")
logging.debug(cfg)
# load bands file
with open("cfg/bands.json") as json_bands:
    band_frequencies = json.load(json_bands)

# load mode file
with open("cfg/modes.json") as json_modes:
    modes_frequencies = json.load(json_modes)

# load continents-cq file
with open("cfg/continents.json") as json_continents:
    continents_cq = json.load(json_continents)

#load visitour counter
visits_file_path = "data/visits.json"
try:
    # Load the visits data from the file
    with open(visits_file_path) as json_visitors:
        visits = json.load(json_visitors)
except FileNotFoundError:
    # If the file does not exist, create an empty visits dictionary
    visits = {}

#save visits
def save_visits():
    with open(visits_file_path, "w") as json_file:
        json.dump(visits, json_file)
    logging.info('visit saved on: '+ visits_file_path)

# saving scheduled
def schedule_save():
    save_visits()
    threading.Timer(1000, schedule_save).start()

# Start scheduling
schedule_save()


# read and set default for enabling cq filter
if cfg.get("enable_cq_filter"):
    enable_cq_filter = cfg["enable_cq_filter"].upper()
else:
    enable_cq_filter = "N"

# define country table for search info on callsigns
pfxt = prefix_table()

# create object query manager
qm = query_manager()

# the main query to show spots
# it gets url parameter in order to apply the build the right query
# and apply the filter required. It returns a json with the spots
def spotquery(parameters):
    try:

        if 'callsign' in parameters:
            logging.debug('search callsign')
            query_string = query_build_callsign(logger,parameters['callsign'] )
        else:
            logging.debug('search eith other filters')
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
    threading.Timer(12 * 3600, get_adxo).start()

get_adxo()




# create data provider for charts
heatmap_cbp = ContinentsBandsProvider(logger, qm, continents_cq, band_frequencies)
bar_graph_spm = SpotsPerMounthProvider(logger, qm)
line_graph_st = SpotsTrend(logger, qm)
bubble_graph_hb = HourBand(logger, qm, band_frequencies)
geo_graph_wdsl = WorldDxSpotsLive(logger, qm, pfxt)

# ROUTINGS
@app.route("/spotlist", methods=["POST"])
@csrf.exempt
def spotlist():
    logger.debug(request.json)
    response = flask.Response(json.dumps(spotquery(request.json)))
    return response


def who_is_connected():
    host=cfg["telnet"]["host"]
    port=cfg["telnet"]["port"]
    user=cfg["telnet"]["user"]
    password=cfg["telnet"]["password"]
    response = who(host, port, user, password)
    logger.debug("list of connected clusters:")
    logger.debug(response)
    return response

#Calculate nonce token used in inline script and in csp "script-src" header
def get_nonce():
    global inline_script_nonce
    inline_script_nonce = secrets.token_hex()
    return inline_script_nonce

#check if it is a unique visitor
def visitor_count():
    user_ip =request.environ.get('HTTP_X_REAL_IP', request.remote_addr)   
    if user_ip not in visits:
        visits[user_ip] = 1
    else:
        visits[user_ip] += 1        
    
@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def spots():
    
    
    visitor_count();

    response = flask.Response(
        render_template(
            "index.html",
            inline_script_nonce=get_nonce(),
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["host"]+":"+cfg["telnet"]["port"],
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
    return app.send_static_file("data/world.json")

@app.route("/plots.html")
def plots():
    whoj = who_is_connected()
    response = flask.Response(
        render_template(
            "plots.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["host"]+":"+cfg["telnet"]["port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),                     
            who=whoj,
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
        logging.debug("connection to: " + url)
        req = requests.get(url)
        logger.debug(req.content)
        solar_data = xmltodict.parse(req.content)    
        logger.debug(solar_data)

    except Exception as e1:
        logging.error(e1)

    response = flask.Response(
        render_template(
            "propagation.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["host"]+":"+cfg["telnet"]["port"],
            mail=cfg["mail"],
            menu_list=cfg["menu"]["menu_list"],
            visits=len(visits),                     
            solar_data=solar_data
        )
    )

    #response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route("/cookies.html", methods=["GET"])
def cookies():
    response = flask.Response(
        render_template(
            "cookies.html",
            inline_script_nonce=get_nonce(),          
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["host"]+":"+cfg["telnet"]["port"],
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
            telnet=cfg["telnet"]["host"]+":"+cfg["telnet"]["port"],
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
    # payload=spotquery()
    callsign = request.args.get("c")
    response = flask.Response(
        render_template(
            "callsign.html",
            inline_script_nonce=get_nonce(),              
            mycallsign=cfg["mycallsign"],
            telnet=cfg["telnet"]["host"]+":"+cfg["telnet"]["port"],
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
    #continent = request.args.get("continent")
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
   app.run(host="0.0.0.0")
