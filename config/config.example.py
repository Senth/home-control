# Logging
# LOG_VERBOSE = True, same as running --verbose. Defaults to False.
# LOG_DEBUG = True, same as running --debug (also turns on --verbose). Defaults to False.
# Running --verbose or --debug through the command line will always override this setting.
LOG_VERBOSE = False
LOG_DEBUG = False

# IKEA Tradfri gateway information
TRADFRI_HOST = "192.168.0.5"
TRADFRI_IDENTITY = ""
TRADFRI_KEY = ""

# Philiphs Hue settings
HUE_HOST = "192.168.0.6"
HUE_USERNAME = ""

# Your location in LAT and LONG, used both for sunset/sunrise and weather
LAT = 30
LONG = 30

# (Optional) Web Api port - The web api is used for controlling home-control through http requests. Defaults to 5001.
WEB_API_PORT = 5001

# (Optional) Stats .csv file for personal statistics. Defaults to ""
STATS_FILE = "/home/senth/personal-data.csv"

# Unifi settings
UNIFI_USERNAME = ""
UNIFI_PASSWORD = ""
UNIFI_HOST = "192.168.0.254"

# (Optional) Unifi port. Defaults to 8444
UNIFI_PORT = 8444

# (Optional) Site Id. Defaults to 'default'
UNIFI_SITE_ID = "default"

# (Optional) time for inactive guests. Defaults to 300
UNIFI_GUEST_INACTIVE_TIME = 300
