__author__ = "IU1BOW - Corrado"
import flask
from flask import request, render_template, redirect, url_for, flash # Added redirect, url_for, flash
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
import os, shutil
from lib.dxtelnet import fetch_who_and_version
from lib.adxo import get_adxo_events
from lib.qry import query_manager
from lib.cty import prefix_table
from lib.plot_data_provider import ContinentsBandsProvider, SpotsPerMounthProvider, SpotsTrend, HourBand, WorldDxSpotsLive
from lib.qry_builder import query_build, query_build_callsign, query_build_callsing_list
from lib.bandplan import BandPlan
from lib.util import copytree, check_create_path

# Start additions for Login and Administration
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from lib.user_manager import UserManager, User
from lib.forms import LoginForm, ChangePasswordForm, UserForm  
# End additions for Login and Administration

TIMER_VISIT = 1000
TIMER_ADXO = 12 * 3600
TIMER_WHO = 7 * 60

LOCAL = 'local'
LOCAL_CFG = LOCAL+'/cfg'
LOCAL_DATA = LOCAL+'/data'
LOCAL_LOG = LOCAL+'/log'


if check_create_path(LOCAL_CFG) == 1:
    print("Creating local path")
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
    SESSION_COOKIE_HTTPONLY=False, # To access the cookie from JS (if needed)
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
    #exit(1)
    cfg = None

    
def save_config(new_cfg_data):
    try:
        with open(LOCAL_CFG+"/config.json", 'w') as f:
            json.dump(new_cfg_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

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
enable_cq_filter = "N"
if cfg is not None:
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
    if cfg is None:
        host = ""
        port = ""
        user = ""
        password = ""
    else:
        host = cfg["telnet"]["telnet_host"]
        port = cfg["telnet"]["telnet_port"]
        user = cfg["telnet"]["telnet_user"]
        password = cfg["telnet"]["telnet_password"]

    timeout_seconds = 10  # Set the desired timeout

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

# --- Start Login and Administration Integration ---

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # The view to redirect to for login
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

user_manager = UserManager() # Initialize the user manager

# Check and create the default admin user if it doesn't exist
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'password' # This password MUST be changed

# Instead of @app.before_first_request, we check and create the admin user here.
# This runs when the module is imported, which happens when 'flask run' is used.
admin_user = user_manager.get_user_by_username(DEFAULT_ADMIN_USERNAME)
if not admin_user:
    logger.warning(f"Creating default administrator user '{DEFAULT_ADMIN_USERNAME}'.")
    success, message = user_manager.add_user(
        DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, "admin", must_change_password=True
    )
    if success:
        logger.info(message)
    else:
        logger.error(f"Error creating default admin user: {message}")

@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user_by_id(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = user_manager.verify_user(username, password)
        if user:
            login_user(user)
            logger.info(f"User {username} logged in successfully.")
            flash('Login successful!', 'success')
            
            # Redirect to password change if required
            if user.must_change_password:
                return redirect(url_for('change_password'))
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('spots')) # Redirect to the requested page or home
        else:
            flash('Login failed. Check your username and password.', 'danger')
            logger.warning(f"Login attempt failed for username: {username}")
    return render_template('login.html', form=form, inline_script_nonce=get_nonce())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('spots'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data

        # Verify old password
        if not user_manager.verify_user(current_user.username, old_password):
            flash('Old password is not correct.', 'danger')
            return render_template('change_password.html', form=form, inline_script_nonce=get_nonce())
        
        # Update password
        success, message = user_manager.update_user_password(current_user.username, new_password, set_must_change_false=True)
        if success:
            flash('Password changed successfully! Please log in again with your new password.', 'success')
            logout_user() # Force logout to make them log in with new password
            return redirect(url_for('login'))
        else:
            flash(f'Error changing password: {message}', 'danger')
            logger.error(f"Password change error for {current_user.username}: {message}")
            
    return render_template('change_password.html', form=form, inline_script_nonce=get_nonce())

@app.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    # Check user role: only admins can access
    if current_user.profile != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        logger.warning(f"Unauthorized access to admin dashboard for user: {current_user.username}")
        return redirect(url_for('spots')) # Or an error page
    
    users = user_manager.get_all_users()
    add_user_form = UserForm() # Form for adding/modifying users
    
    if cfg is None:
        mycallsign="Init mode"
        menu_list=[]
    else:
        mycallsign=cfg["mycallsign"]
        menu_list=cfg["menu"]["menu_list"]

    return render_template('admin.html', 
                           inline_script_nonce=get_nonce(), 
                           users=users,
                           add_user_form=add_user_form,
                           mycallsign=mycallsign,
                           menu_list=menu_list,
                           cfg=json.dumps(cfg, indent=2),
                           visits=len(visits))

@app.route('/admin/add_user', methods=['POST'])
@login_required
def admin_add_user():
    if current_user.profile != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('admin_dashboard'))

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        profile = form.profile.data
        
        success, message = user_manager.add_user(username, password, profile)
        if success:
            flash(f'User "{username}" added successfully.', 'success')
        else:
            flash(f'Error: {message}', 'danger')
            logger.error(f"Error adding user {username} by admin: {message}")
    else:
        # If validation fails, flash form errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in field '{field}': {error}", 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<username>', methods=['POST'])
@login_required
def admin_delete_user(username):
    if current_user.profile != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if username == current_user.username:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin_dashboard'))

    success, message = user_manager.delete_user(username)
    if success:
        flash(f'User "{username}" deleted successfully.', 'success')
    else:
        flash(f'Error: {message}', 'danger')
        logger.error(f"Error deleting user {username} by admin: {message}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_user_password/<username>', methods=['POST'])
@login_required
def admin_update_user_password(username):
    if current_user.profile != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # This requires a separate form or sending the password via AJAX/form
    # For simplicity, here I assume the password is passed as part of the form request
    # In a real application, you would use a dedicated form.
    new_password = request.form.get('new_password_for_' + username)
    
    if new_password:
        success, message = user_manager.update_user_password(username, new_password, set_must_change_false=False)
        if success:
            flash(f'Password for "{username}" updated successfully.', 'success')
        else:
            flash(f'Error updating password: {message}', 'danger')
            logger.error(f"Error updating password for {username} by admin: {message}")
    else:
        flash('New password not provided.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_user_profile/<username>', methods=['POST'])
@login_required
def admin_update_user_profile(username):
    if current_user.profile != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    new_profile = request.form.get('new_profile_for_' + username) # Name of the field in the form
    
    if new_profile:
        success, message = user_manager.update_user_profile(username, new_profile)
        if success:
            flash(f'Profile for "{username}" updated successfully to "{new_profile}".', 'success')
        else:
            flash(f'Error updating profile: {message}', 'danger')
            logger.error(f"Error updating profile for {username} by admin: {message}")
    else:
        flash('New profile not provided.', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_config', methods=['POST'])
@login_required 
#@admin_required # Se solo gli admin possono modificare la config
def admin_update_config():
    global cfg # Dichiara che userai la variabile globale 'cfg'

    if request.method == 'POST':
        configurations_data = request.form.get('configurations_data')

        if not configurations_data:
            flash('No configuration data received.', 'error')
            return redirect(url_for('admin_dashboard'))

        try:
            # Tenta di parsare la stringa JSON
            new_cfg = json.loads(configurations_data)

            # Qui puoi aggiungere validazioni aggiuntive al JSON se necessario
            # es: if "mycallsign" not in new_cfg: ...

            if save_config(new_cfg):
                cfg = new_cfg # Aggiorna la variabile globale cfg
                flash('Configuration updated!', 'success')
            else:
                flash('Error saving configuration.', 'error')

        except json.JSONDecodeError as e:
            flash(f'Not valid JSON: {e}', 'error')
        except Exception as e:
            flash(f'Unexpected error: {e}', 'error')

    return redirect(url_for('admin_dashboard'))

# --- End Login and Administration Integration ---


# ROUTINGS
@app.route("/spotlist", methods=["POST"])
@csrf.exempt
def spotlist():
    logger.debug(request.json)
    if cfg is not None:
        response = flask.Response(json.dumps(spotquery(request.json)))
    else:
        response = None
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
            current_user=current_user # Pass the current_user object to the template
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
            current_user=current_user # Pass the current_user object to the template
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
            solar_data=solar_data,
            current_user=current_user # Pass the current_user object to the template
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
            bandplan_svg=bandplan_file,
            current_user=current_user # Pass the current_user object to the template
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
            current_user=current_user # Pass the current_user object to the template                  
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
            current_user=current_user # Pass the current_user object to the template                 
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
            current_user=current_user # Pass the current_user object to the template
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
    form-action 'self';\
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
