from pathlib import Path

from blulib.config_parser import ConfigParser
from tealprint import TealPrint
from tealprint.tealprint import TealLevel

from ..config import General, Hue, Location, Unifi, config


class ConfigGateway:
    def __init__(self) -> None:
        self.path = Path.home().joinpath(f".{config.app_name}.cfg")
        self.parser = ConfigParser()

    def check_config_exists(self) -> None:
        if not self.path.exists():
            TealPrint.warning(f"Could not find the configuration file: {self.path}", exit=True)

    def read(self) -> None:
        self.parser.read(self.path)

    def get_general(self) -> General:
        general = General()
        self.parser.to_object(
            general,
            "General",
            "int:port",
            "log_level",
            "stats_file",
        )

        # Convert log_level str to TealLevel
        if isinstance(general.log_level, str):
            general.log_level = TealLevel[general.log_level]

        return general

    def get_hue(self) -> Hue:
        hue = Hue()
        self.parser.to_object(
            hue,
            "Hue",
            "host",
            "username",
        )

        if not hue.host:
            self._print_missing("Hue", "host")
        if not hue.username:
            self._print_missing("Hue", "username")

        return hue

    def get_location(self) -> Location:
        location = Location()
        self.parser.to_object(
            location,
            "Location",
            "lat",
            "long",
        )

        if not location.lat:
            self._print_missing("Location", "lat")
        if not location.long:
            self._print_missing("Location", "long")

        return location

    def get_unifi(self) -> Unifi:
        unifi = Unifi()
        self.parser.to_object(
            unifi,
            "Unifi",
            "username",
            "password",
            "host",
            "int:port",
            "site_id",
            "int:guest_inactive_time",
        )

        if not unifi.username:
            self._print_missing("Unifi", "username")
        if not unifi.password:
            self._print_missing("Unifi", "password")
        if not unifi.host:
            self._print_missing("Unifi", "host")

        return unifi

    def _print_missing(self, section: str, var_name: str) -> None:
        TealPrint.warning(
            f"Missing '{var_name} under [{section}] in your configuration {self.path}. Please add it.", exit=True
        )
