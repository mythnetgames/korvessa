# Automatically enable mapper and cleanup scripts on server start
STARTUP_SCRIPTS = [
    "scripts.map_enable_script.MapEnableScript",
    "scripts.cleanup_idle_sessions.IdleSessionCleanup",
    "scripts.cleanup_idle_sessions.PhantomCharacterCleanup",
]
r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Korvessa"
# Short one-sentence blurb describing your game. Shown under the title
# on the website and could be used in online listings of your game etc.
GAME_SLOGAN = "May He Watch over you."
# The url address to your server, like mymudgame.com. This should be the publicly
# visible location. This is used e.g. on the web site to show how you connect to the
# game over telnet. Default is localhost (only on your machine).
SERVER_HOSTNAME = "korvessarpi.org"
# Lockdown mode will cut off the game from any external connections
# and only allow connections from localhost. Requires a cold reboot.
LOCKDOWN_MODE = False
# Allow new account registration via the website and the `create` command
# (October 18, 2025: Enabled for Cloudflare Turnstile integration testing)
NEW_ACCOUNT_REGISTRATION_ENABLED = True
#Time Zone
TIME_ZONE = "America/Chicago"
# Activate telnet service
TELNET_ENABLED = True
# A list of ports the Evennia telnet server listens on Can be one or many.
TELNET_PORTS = [4000]
# This is a security setting protecting against host poisoning
# attacks.  It defaults to allowing all. In production, make
# sure to change this to your actual host addresses/IPs.
ALLOWED_HOSTS = ["korvessarpi.org", "www.korvessarpi.org", "127.0.0.1", "localhost"]
# This is a security setting protecting against DJANGO CSRF nonsense
CSRF_TRUSTED_ORIGINS = ['https://korvessarpi.org', 'https://3.3.15.195.148']
# Start the evennia webclient. This requires the webserver to be running and
# offers the fallback ajax-based webclient backbone for browsers not supporting
# the websocket one.
WEBCLIENT_ENABLED = True

# Use secure websocket on port 8443 (CloudFlare-proxied port)
# CloudFlare handles SSL termination and proxies to backend port 4002
WEBSOCKET_CLIENT_URL = "wss://korvessarpi.org:4002"

# Default exit typeclass
DEFAULT_EXIT_TYPECLASS = "typeclasses.exits.Exit"

######################################################################
# Account and Character Management
######################################################################

# Set multisession mode to 1: Account-based login with single character
# This enables proper account/character separation for resleeving mechanics
# Mode 1: Login with account (email), then select/create character
MULTISESSION_MODE = 1

# Enable auto-puppeting for seamless login experience
# Characters will be created/managed through resleeving system
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False  # We'll handle this custom
AUTO_PUPPET_ON_LOGIN = False  # Let at_post_login handle character selection/creation

# Default starting location for new characters
# Override in secret_settings.py for your specific deployment
# If not set, defaults to Limbo (#2)
# START_LOCATION = "#2"  # Example: set to your spawn room

# Use our custom email-based login system
CMDSET_UNLOGGEDIN = "commands.unloggedin_email.UnloggedinEmailCmdSet"
CONNECTION_SCREEN_MODULE = "server.conf.connection_screens"

######################################################################
# Django web features
######################################################################

# Configure authentication backends for email-only login
AUTHENTICATION_BACKENDS = [
    "web.utils.auth_backends.EmailAuthenticationBackend",  # Email-based login only
]

######################################################################
# Cloudflare Turnstile Configuration
######################################################################

# Cloudflare Turnstile keys for CAPTCHA verification
# Get your keys from: https://dash.cloudflare.com/?to=/:account/turnstile
# NOTE: These should be moved to secret_settings.py in production
TURNSTILE_SITE_KEY = ""  # Public site key (visible in HTML)
TURNSTILE_SECRET_KEY = ""  # Secret key (server-side only)

######################################################################
# Django web features
######################################################################

# While DEBUG is False, show a regular server error page on the web
# stuff, email the traceback to the people in the ADMINS tuple
# below. If True, show a detailed traceback for the web
# browser to display. Note however that this will leak memory when
# active, so make sure to turn it off for a production server!
DEBUG = False

######################################################################
# Session and Idle Timeout Settings
######################################################################

# Automatically disconnect idle sessions after 24 hours
# This prevents "ghost" characters when players disconnect without logging out
# Value is in seconds: 24 * 60 * 60 = 86400 seconds
IDLE_TIMEOUT = 86400

# Immediately disconnect players on network disconnect
# Prevents phantom sessions from disconnects
SESSION_DISCONNECT_TIMEOUT = 5  # 5 seconds to detect disconnect

######################################################################
# Game Time Configuration
######################################################################

# Time factor: 1.0 = real time, >1 = faster, <1 = slower
# Set to 3.0 so 1 real month = ~3 game months (Korvessan calendar)
TIME_FACTOR = 3.0

# Game time epoch in seconds since Unix epoch
# Adjusted to match January 12, 1970 at current time (adding 10 minutes)
TIME_GAME_EPOCH = -3114700


######################################################################
# Prototype Modules
######################################################################

# Add chrome prototypes to the default prototype modules
PROTOTYPE_MODULES = ["world.prototypes", "world.chrome_prototypes"]

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")


# Startup check: ensure SQLite database file (if used) is writable so the
# server fails with a clear message instead of later raising a confusing
# OperationalError during login or save operations.
try:
    from pathlib import Path
    from django.conf import settings as _dj_settings

    _db = getattr(_dj_settings, 'DATABASES', {}).get('default', {})
    _engine = _db.get('ENGINE', '')
    if _engine.endswith('sqlite3'):
        _name = _db.get('NAME')
        if _name and _name != ':memory:':
            _path = Path(str(_name))
            # Ensure parent directory exists
            try:
                _path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as _e:
                print(f"FATAL: Could not ensure database directory exists: {_path.parent} ({_e})")
                raise SystemExit("Database directory not writable or creatable. Fix permissions and restart.")

            # Try opening the DB file for append (will create if missing). This tests write
            # permission on the filesystem and will surface if the file or mount is read-only.
            try:
                with open(_path, 'a'):
                    pass
            except Exception as _e:
                print(f"FATAL: SQLite database file is not writable: {_path} ({_e})")
                print("Fix by adjusting ownership/permissions or moving the DB to a writable path.")
                raise SystemExit("SQLite database not writable; aborting startup.")
except Exception:
    # Don't raise here if Django isn't fully configured yet; just allow startup to continue
    # and let more specific errors surface during normal operation.
    pass
