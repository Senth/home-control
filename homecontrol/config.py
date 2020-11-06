from os import path
import sys
import site
import importlib.util
import argparse

_app_name = __package__.replace("_", "-")
_config_dir = path.join("config", _app_name)
_config_file = path.join(_config_dir, "config.py")
_example_file = path.join(_config_dir, "config.example.py")

# Search for config file in sys path
_sys_config = path.join(sys.prefix, _config_file)
_user_config_file = path.join(site.getuserbase(), _config_file)
_config_file = ""
if path.exists(_sys_config):
    _config_file = _sys_config
elif path.exists(_user_config_file):
    _config_file = _user_config_file
# User hasn't configured the program yet
else:
    _sys_config_example = path.join(sys.prefix, _example_file)
    _user_config_example = path.join(site.getuserbase(), _example_file)
    if not path.exists(_sys_config_example) and not path.exists(_user_config_example):
        print(
            f"Error: no configuration found. It should be here: '{_user_config_file}'"
        )
        print("run: locate " + _example_file)
        print("This should help you find the current config location.")
        print(
            f"Otherwise you can download the config.example.py from https://github.com/Senth/{_app_name}/tree/main/config and place it in the correct location"
        )
        sys.exit(1)

    print("This seems like it's the first time you run this program.")
    print(
        f"For this program to work properly you have to configure it by editing '{_user_config_file}'"
    )
    print(
        "In the same folder there's an example file 'config.example.py' you can copy to 'config.py'."
    )
    sys.exit(0)

_spec = importlib.util.spec_from_file_location("config", _user_config_file)
_user_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_user_config)


def _print_missing(variable_name):
    print(f"Missing {variable_name} variable in config file: {_user_config_file}")
    print("Please add it to you config.py again to continue")
    sys.exit(1)


class Config:
    def __init__(self, user_config):
        self._user_config = user_config
        self._set_default_values()
        self._get_optional_variables()
        self._check_required_variables()
        self._parse_args()
        self.app_name = __package__.replace("_", "-")

    def _parse_args(self):
        # Get arguments first to get verbosity before we get everything else
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Prints out helpful messages. (NOT IMPLEMENTED YET)",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Turn on debug messages. This automatically turns on --verbose as well. (NOT IMPLEMENTED YET)",
        )

        _args = parser.parse_args()
        self._add_args_settings(_args)

    def _add_args_settings(self, args):
        """Set additional configuration from script arguments

        Args:
            args (list): All the parsed arguments
        """
        self.verbose = args.verbose
        self.debug = args.debug

        if args.debug:
            self.verbose = True

    def _set_default_values(self):
        """Set default values for variables"""
        self.unifi = Unifi()
        self.location = Location()
        self.tradfri = Tradfri()
        self.stats_file = False

    def _get_optional_variables(self):
        """Get optional values from the config file"""
        try:
            self.unifi.port = _user_config.UNIFI_PORT
        except AttributeError:
            pass

        try:
            self.unifi.site_id = _user_config.UNIFI_SITE_ID
        except AttributeError:
            pass

        try:
            self.stats_file = _user_config.STATS_FILE
        except AttributeError:
            pass

    def _check_required_variables(self):
        """Check that all required variables are set in the user config file"""
        try:
            self.tradfri.host = _user_config.TRADFRI_HOST
        except AttributeError:
            _print_missing("TRADFRI_HOST")

        try:
            self.tradfri.identity = _user_config.TRADFRI_IDENTITY
        except AttributeError:
            _print_missing("TRADFRI_IDENTITY")

        try:
            self.tradfri.key = _user_config.TRADFRI_KEY
        except AttributeError:
            _print_missing("TRADFRI_KEY")

        try:
            self.location.lat = _user_config.LAT
        except AttributeError:
            _print_missing("LAT")

        try:
            self.location.long = _user_config.LONG
        except AttributeError:
            _print_missing("LONG")

        try:
            self.unifi.username = _user_config.UNIFI_USERNAME
        except AttributeError:
            _print_missing("UNIFI_USERNAME")

        try:
            self.unifi.password = _user_config.UNIFI_PASSWORD
        except AttributeError:
            _print_missing("UNIFI_PASSWORD")

        try:
            self.unifi.host = _user_config.UNIFI_HOST
        except AttributeError:
            _print_missing("UNIFI_HOST")


class Tradfri:
    def __init__(self):
        self.host = ""
        self.identity = ""
        self.key = ""


class Location:
    def __init__(self):
        self.long = ""
        self.lat = ""

    def weather_url(self):
        return f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{self.long}/lat/{self.lat}/data.json"


class Unifi:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.host = ""
        self.port = 8444
        self.site_id = "default"


global config
config = Config(_user_config)
