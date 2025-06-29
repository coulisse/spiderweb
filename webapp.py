import flask
from flask import request, render_template, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_minify import minify
import datetime
import secrets
import json
import logging
import logging.config
import requests
import xmltodict
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Assuming these are in the lib directory
import lib.constants as CONST
from lib.bandplan import BandPlan
from lib.util import copytree, check_create_path
from lib.user_manager import UserManager
from lib.forms import LoginForm, ChangePasswordForm, UserForm
from lib.datamanager import DataManager
from lib.backgroundtaskmanager import BackgroundTaskManager
from lib.appconfig import AppConfig

# --- Logging Setup ---
# Step 1: Check if the log configuration file exists
try:
    logging.config.fileConfig(CONST.INI_CONFIG, disable_existing_loggers=True)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured using file: %s", CONST.INI_CONFIG)
except FileNotFoundError:
    # Step 2: If the file doesn't exist, set up a basic logging configuration
    logging.basicConfig(
        level=logging.INFO,  # Set the default logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Log to console
        ]
    )
    logger = logging.getLogger(__name__)
    logger.warning("Log configuration file not found (%s) Using basic logging configuration.", CONST.INI_CONFIG)
except Exception as e:
    # Catch other potential errors during file configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    logger.error("Error loading log configuration from file (%s): %s. Using basic error logging.", CONST.INI_CONFIG, e)

class FlaskApp:
    """Main Flask application class."""
    def __init__(self, logger):
        self.logger = logger
        self.app = flask.Flask(__name__)
        self.app_config_manager = AppConfig(logger)
        self.data_manager = DataManager(logger, self.app_config_manager)
        self.background_tasks = BackgroundTaskManager(logger, self.data_manager, self.app_config_manager)
        self.user_manager = UserManager()
        self.inline_script_nonce = ""
        self._setup_app()
        self._setup_login_manager()
        self._setup_routes()

    def _setup_app(self):
        """Sets up Flask application configurations."""
        self.app.config["SECRET_KEY"] = secrets.token_hex(16)
        self.app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=False,
            SESSION_COOKIE_SAMESITE="Strict",
        )

        try:
            with open(CONST.VERSION_FILE, "r") as version_file:
                self.app.config["VERSION"] = version_file.read().strip()
        except Exception as e:
            self.logger.error(f"Error reading version file: {e}")
            self.app.config["VERSION"] = "Unknown"

        self.logger.info(f"Version: {self.app.config['VERSION']}")

        self.csrf = CSRFProtect(self.app) # Assign to self.csrf

        if self.app.config.get("DEBUG"):
            minify(app=self.app, html=False, js=False, cssless=False)
        else:
            minify(app=self.app, html=True, js=True, cssless=False)

        self.app.jinja_env.trim_blocks = True
        self.app.jinja_env.lstrip_blocks = True

        try:
            bp = BandPlan(self.logger, self.data_manager.band_frequencies, self.data_manager.modes_frequencies, 'static/images/icons/icon-512x512-transparent.png')
            bp.create(CONST.BANDPLAN)
            del bp
        except Exception as e:
            self.logger.error(f"Bandplan not created: {e}")

    def _setup_login_manager(self):
        """Sets up Flask-Login manager."""
        login_manager = LoginManager()
        login_manager.init_app(self.app)
        login_manager.login_view = 'login'
        login_manager.login_message = "Please log in to access this page."
        login_manager.login_message_category = "info"

        @login_manager.user_loader
        def load_user(user_id):
            return self.user_manager.get_user_by_id(user_id)

        admin_user = self.user_manager.get_user_by_username(CONST.DEFAULT_ADMIN_USERNAME)
        if not admin_user:
            self.logger.warning(f"Creating default administrator user '{CONST.DEFAULT_ADMIN_USERNAME}'.")
            success, message = self.user_manager.add_user(
                CONST.DEFAULT_ADMIN_USERNAME, CONST.DEFAULT_ADMIN_PASSWORD, "admin", must_change_password=True
            )
            if success:
                self.logger.info(message)
            else:
                self.logger.error(f"Error creating default admin user: {message}")

    def get_nonce(self):
        """Generates and returns a nonce for inline scripts."""
        self.inline_script_nonce = secrets.token_hex()
        return self.inline_script_nonce

    def _setup_routes(self):
        """Defines all application routes.
        This method will attach routes to self.app (the Flask instance).
        """

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            form = LoginForm()
            if form.validate_on_submit():
                username = form.username.data
                password = form.password.data
                user = self.user_manager.verify_user(username, password)
                if user:
                    login_user(user)
                    self.logger.info(f"User {username} logged in successfully.")
                    flash('Login successful!', 'success')
                    if user.must_change_password:
                        return redirect(url_for('change_password'))
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('spots'))
                else:
                    flash('Login failed. Check your username and password.', 'danger')
                    self.logger.warning(f"Login attempt failed for username: {username}")
            return render_template('login.html', form=form, inline_script_nonce=self.get_nonce())

        @self.app.route('/logout')
        @login_required
        def logout():
            logout_user()
            flash('You have been logged out.', 'info')
            return redirect(url_for('spots'))

        @self.app.route('/change_password', methods=['GET', 'POST'])
        @login_required
        def change_password():
            form = ChangePasswordForm()
            if form.validate_on_submit():
                old_password = form.old_password.data
                new_password = form.new_password.data
                if not self.user_manager.verify_user(current_user.username, old_password):
                    flash('Old password is not correct.', 'danger')
                    return render_template('change_password.html', form=form, inline_script_nonce=self.get_nonce())
                success, message = self.user_manager.update_user_password(current_user.username, new_password, set_must_change_false=True)
                if success:
                    flash('Password changed successfully! Please log in again with your new password.', 'success')
                    logout_user()
                    return redirect(url_for('login'))
                else:
                    flash(f'Error changing password: {message}', 'danger')
                    self.logger.error(f"Password change error for {current_user.username}: {message}")
            return render_template('change_password.html', form=form, inline_script_nonce=self.get_nonce())

        @self.app.route('/admin', methods=['GET'])
        @login_required
        def admin_dashboard():
            if current_user.profile != 'admin':
                flash('You do not have permission to access this page.', 'danger')
                self.logger.warning(f"Unauthorized access to admin dashboard for user: {current_user.username}")
                return redirect(url_for('spots'))

            users = self.user_manager.get_all_users()
            add_user_form = UserForm()

            cfg_data = self.app_config_manager.cfg
            mycallsign = cfg_data["mycallsign"] if cfg_data else "Init mode"
            menu_list = cfg_data["menu"]["menu_list"] if cfg_data else []

            return render_template('admin.html',
                                   inline_script_nonce=self.get_nonce(),
                                   users=users,
                                   add_user_form=add_user_form,
                                   mycallsign=mycallsign,
                                   menu_list=menu_list,
                                   cfg=json.dumps(cfg_data, indent=2),
                                   visits=len(self.data_manager.visits))

        @self.app.route('/admin/add_user', methods=['POST'])
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
                success, message = self.user_manager.add_user(username, password, profile)
                if success:
                    flash(f'User "{username}" added successfully.', 'success')
                else:
                    flash(f'Error: {message}', 'danger')
                    self.logger.error(f"Error adding user {username} by admin: {message}")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error in field '{field}': {error}", 'danger')
            return redirect(url_for('admin_dashboard'))

        @self.app.route('/admin/delete_user/<username>', methods=['POST'])
        @login_required
        def admin_delete_user(username):
            if current_user.profile != 'admin':
                flash('You do not have permission to perform this action.', 'danger')
                return redirect(url_for('admin_dashboard'))

            if username == current_user.username:
                flash('You cannot delete your own account!', 'danger')
                return redirect(url_for('admin_dashboard'))

            success, message = self.user_manager.delete_user(username)
            if success:
                flash(f'User "{username}" deleted successfully.', 'success')
            else:
                flash(f'Error: {message}', 'danger')
                self.logger.error(f"Error deleting user {username} by admin: {message}")
            return redirect(url_for('admin_dashboard'))

        @self.app.route('/admin/update_user_password/<username>', methods=['POST'])
        @login_required
        def admin_update_user_password(username):
            if current_user.profile != 'admin':
                flash('You do not have permission to perform this action.', 'danger')
                return redirect(url_for('admin_dashboard'))

            new_password = request.form.get('new_password_for_' + username)
            if new_password:
                success, message = self.user_manager.update_user_password(username, new_password, set_must_change_false=False)
                if success:
                    flash(f'Password for "{username}" updated successfully.', 'success')
                else:
                    flash(f'Error updating password: {message}', 'danger')
                    self.logger.error(f"Error updating password for {username} by admin: {message}")
            else:
                flash('New password not provided.', 'danger')
            return redirect(url_for('admin_dashboard'))

        @self.app.route('/admin/update_user_profile/<username>', methods=['POST'])
        @login_required
        def admin_update_user_profile(username):
            if current_user.profile != 'admin':
                flash('You do not have permission to perform this action.', 'danger')
                return redirect(url_for('admin_dashboard'))

            new_profile = request.form.get('new_profile_for_' + username)
            if new_profile:
                success, message = self.user_manager.update_user_profile(username, new_profile)
                if success:
                    flash(f'Profile for "{username}" updated successfully to "{new_profile}".', 'success')
                else:
                    flash(f'Error updating profile: {message}', 'danger')
                    self.logger.error(f"Error updating profile for {username} by admin: {message}")
            else:
                flash('New profile not provided.', 'danger')
            return redirect(url_for('admin_dashboard'))

        @self.app.route('/admin/update_config', methods=['POST'])
        @login_required
        def admin_update_config():
            if current_user.profile != 'admin':
                flash('You do not have permission to perform this action.', 'danger')
                return redirect(url_for('admin_dashboard'))

            configurations_data = request.form.get('configurations_data')
            if not configurations_data:
                flash('No configuration data received.', 'error')
                return redirect(url_for('admin_dashboard'))

            try:
                new_cfg = json.loads(configurations_data)
                if self.app_config_manager.save_config(new_cfg):
                    self.data_manager._init_data_objects()
                    flash('Configuration updated!', 'success')
                else:
                    flash('Error saving configuration.', 'error')
            except json.JSONDecodeError as e:
                flash(f'Not valid JSON: {e}', 'error')
            except Exception as e:
                flash(f'Unexpected error: {e}', 'error')
            return redirect(url_for('admin_dashboard'))

        @self.app.route("/spotlist", methods=["POST"])
        @self.csrf.exempt
        def spotlist():
            self.logger.debug(request.json)
            if self.app_config_manager.cfg is not None:
                response_data = self.data_manager.spotquery(request.json)
                response = flask.Response(json.dumps(response_data))
            else:
                response = flask.Response(status=500)
            return response

        @self.app.route("/", methods=["GET"])
        @self.app.route("/index.html", methods=["GET"])
        def spots():
            self.data_manager.increment_visitor_count(request.environ, request.remote_addr)
            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                flash("Configuration not loaded. Please check server logs.", "danger")
                return render_template("error.html", message="Configuration not loaded.")

            return render_template(
                "index.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                timer_interval=cfg_data["timer"]["interval"],
                adxo_events=self.data_manager.adxo_events,
                continents=self.data_manager.continents_cq,
                bands=self.data_manager.band_frequencies,
                dx_calls=self.data_manager.get_dx_calls(),
                current_user=current_user
            )

        @self.app.route("/service-worker.js", methods=["GET"])
        def sw():
            return self.app.send_static_file("pwa/service-worker.js")

        @self.app.route("/offline.html")
        def root():
            return self.app.send_static_file("html/offline.html")

        @self.app.route("/world.json")
        def world_data():
            return self.app.send_static_file("data/world.json")

        @self.app.route("/plots.html")
        def plots():
            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                return render_template("error.html", message="Configuration not loaded for plots.")

            return render_template(
                "plots.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                who=self.background_tasks.whoj.get("data", []),
                last_updated=self.background_tasks.whoj.get("last_updated", "No data"),
                dxspider_version=self.background_tasks.whoj.get("version", "Unknown"),
                continents=self.data_manager.continents_cq,
                bands=self.data_manager.band_frequencies,
                current_user=current_user
            )

        @self.app.route("/propagation.html")
        def propagation():
            solar_data = {}
            url = CONST.SOLAR_DATA_URL
            try:
                self.logger.debug(f"Connecting to: {url}")
                req = requests.get(url)
                solar_data = xmltodict.parse(req.content)
                self.logger.debug(solar_data)
            except Exception as e:
                self.logger.error(f"Error fetching solar data: {e}")

            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                return render_template("error.html", message="Configuration not loaded for propagation.")

            return render_template(
                "propagation.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                solar_data=solar_data,
                current_user=current_user
            )

        @self.app.route("/bandplan.html", methods=["GET"])
        def bandplan():
            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                return render_template("error.html", message="Configuration not loaded for bandplan.")

            return render_template(
                "bandplan.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                bandplan_svg=CONST.BANDPLAN,
                current_user=current_user
            )

        @self.app.route("/cookies.html", methods=["GET"])
        def cookies():
            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                return render_template("error.html", message="Configuration not loaded for cookies.")

            return render_template(
                "cookies.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                current_user=current_user
            )

        @self.app.route("/privacy.html", methods=["GET"])
        def privacy():
            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                return render_template("error.html", message="Configuration not loaded for privacy.")

            return render_template(
                "privacy.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                current_user=current_user
            )

        @self.app.route("/callsign.html", methods=["GET"])
        def callsign_page():
            callsign = request.args.get("c")
            cfg_data = self.app_config_manager.cfg
            if cfg_data is None:
                return render_template("error.html", message="Configuration not loaded for callsign page.")

            return render_template(
                "callsign.html",
                inline_script_nonce=self.get_nonce(),
                mycallsign=cfg_data["mycallsign"],
                telnet=f"{cfg_data['telnet']['telnet_host']}:{cfg_data['telnet']['telnet_port']}",
                mail=cfg_data["mail"],
                menu_list=cfg_data["menu"]["menu_list"],
                visits=len(self.data_manager.visits),
                timer_interval=cfg_data["timer"]["interval"],
                callsign=callsign,
                adxo_events=self.data_manager.adxo_events,
                continents=self.data_manager.continents_cq,
                bands=self.data_manager.band_frequencies,
                current_user=current_user
            )

        @self.app.route('/sitemap.xml')
        def sitemap():
            pages = set()
            for rule in self.app.url_map.iter_rules():
                if "GET" in rule.methods and not rule.arguments:
                    pages.add(url_for(rule.endpoint, _external=True))

            exclude_list = ['/sitemap.xml', '/admin','/service-worker.js',
                            '/change_password','/login','/logout','/callsign',
                            '/offline.html','/world.json', '/callsign.html']
            pages = {page for page in pages if not any(page.endswith(exclude) for exclude in exclude_list)}

            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            for page in pages:
                priority = 1.0 if page.endswith('/index.html') or page.endswith('/') else 0.8
                xml_content += f'    <url>\n'
                xml_content += f'        <loc>{page}</loc>\n'
                xml_content += f'        <lastmod>{datetime.datetime.now().date()}</lastmod>\n'
                xml_content += f'        <changefreq>monthly</changefreq>\n'
                xml_content += f'        <priority>{priority}</priority>\n'
                xml_content += f'    </url>\n'
            xml_content += '</urlset>'

            return flask.Response(xml_content, mimetype='application/xml')

        @self.app.route("/callsign", methods=["GET"])
        def find_callsign_api():
            callsign = request.args.get("c")
            response = self.data_manager.pfxt.find(callsign)
            if response is None:
                response = flask.Response(status=204)
            return response

        @self.app.route("/plot_get_heatmap_data", methods=["POST"])
        @self.csrf.exempt
        def get_heatmap_data():
            continent = request.json['continent']
            self.logger.debug(request.get_json())
            data = self.data_manager.heatmap_cbp.get_data(continent)
            response = flask.Response(json.dumps(data))
            self.logger.debug(response)
            if data is None or len(data) == 0:
                response = flask.Response(status=204)
            return response

        @self.app.route("/plot_get_dx_spots_per_month", methods=["POST"])
        @self.csrf.exempt
        def get_dx_spots_per_month():
            data = self.data_manager.bar_graph_spm.get_data()
            response = flask.Response(json.dumps(data))
            self.logger.debug(response)
            if data is None or len(data) == 0:
                response = flask.Response(status=204)
            return response

        @self.app.route("/plot_get_dx_spots_trend", methods=["POST"])
        @self.csrf.exempt
        def get_dx_spots_trend():
            data = self.data_manager.line_graph_st.get_data()
            response = flask.Response(json.dumps(data))
            self.logger.debug(response)
            if data is None or len(data) == 0:
                response = flask.Response(status=204)
            return response

        @self.app.route("/plot_get_hour_band", methods=["POST"])
        @self.csrf.exempt
        def get_dx_hour_band():
            data = self.data_manager.bubble_graph_hb.get_data()
            response = flask.Response(json.dumps(data))
            self.logger.debug(response)
            if data is None or len(data) == 0:
                response = flask.Response(status=204)
            return response

        @self.app.route("/plot_get_world_dx_spots_live", methods=["POST"])
        @self.csrf.exempt
        def get_world_dx_spots_live():
            data = self.data_manager.geo_graph_wdsl.get_data()
            response = flask.Response(json.dumps(data))
            self.logger.debug(response)
            if data is None or len(data) == 0:
                response = flask.Response(status=204)
            return response

        @self.app.route("/csp-reports", methods=['POST'])
        @self.csrf.exempt
        def csp_reports():
            report_data = request.get_data(as_text=True)
            self.logger.warning("CSP Report: %s", report_data)
            return flask.Response(status=204)

        @self.app.after_request
        def add_security_headers(resp):
            resp.headers["Strict-Transport-Security"] = "max-age=1000"
            resp.headers["X-Xss-Protection"] = "1; mode=block"
            resp.headers["X-Frame-Options"] = "SAMEORIGIN"
            resp.headers["X-Content-Type-Options"] = "nosniff"
            resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            resp.headers["Cache-Control"] = "public, no-cache, must-revalidate, max-age=900"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["ETag"] = self.app.config["VERSION"]

            csp = "\
            default-src 'self';\
            script-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net 'nonce-"+self.inline_script_nonce+"';\
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
            if request.endpoint in ['plots', 'get_heatmap_data', 'get_dx_spots_per_month', 'get_dx_spots_trend', 'get_dx_hour_band', 'get_world_dx_spots_live']:
                self.logger.debug(f"Applying 'unsafe-inline' style-src for endpoint: {request.endpoint}")
                csp = csp.replace(
                    "style-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net;",
                    "style-src 'self' cdnjs.cloudflare.com cdn.jsdelivr.net 'unsafe-inline';"
                )
            resp.headers["Content-Security-Policy"] = csp
            return resp

    def run(self, host="0.0.0.0", port=5000):
        """Runs the Flask application."""
        self.logger.info("Starting SPIDERWEB application.")
        self.app.run(host=host, port=port, debug=self.app.config.get("DEBUG", False))

# --- Application Initialization for 'flask run' and direct execution ---

# Step 1: Ensure local paths exist *before* trying to load config or initialize anything that relies on them.
if check_create_path(CONST.LOCAL_CFG) == 1:
    logger.info("Creating local config path.")
    copytree('cfg', CONST.LOCAL_CFG)
check_create_path(CONST.LOCAL_LOG)
check_create_path(CONST.LOCAL_DATA)

# Step 2: Create the FlaskApp instance. This instance will handle all setup.
_flask_app_wrapper_instance = FlaskApp(logger)

# Step 3: Expose the actual Flask application object.
app = _flask_app_wrapper_instance.app

# --- Direct Execution (optional, for `python webapp2.py`) ---
if __name__ == "__main__":
    # If you run the script directly, this block will execute and start the Flask development server.
    # When using 'flask run', this block is typically not executed by the Flask CLI itself.
    logger.info("Running application via direct script execution (__main__).")
    _flask_app_wrapper_instance.run(debug=app.config.get("DEBUG", False))
