from flask import Flask
from tealprint import TealLevel, TealPrint

from ..config import config
from .color import color_blueprint
from .dim import dim_blueprint
from .effect import effect_blueprint, get_effects_blueprint
from .info import get_info_blueprint
from .kill import kill_blueprint
from .log import log_blueprint
from .mood import mood_blueprint
from .power import power_blueprint


def run_api() -> None:
    TealPrint.debug("Flask API: Initializing")

    api = Flask(__package__)
    api.config["DEBUG"] = config.general.log_level == TealLevel.debug
    # FIXME different logging for --debug, --verbose, and default
    if config.general.log_level == TealLevel.debug:
        log_level = "DEBUG"
    elif config.general.log_level == TealLevel.verbose:
        log_level = "INFO"
    else:
        log_level = "WARNING"
    api.config["LOG_LEVEL"] = log_level

    TealPrint.debug("Flask API: Registering Blueprints")
    # Register blueprints
    # GET
    api.register_blueprint(get_info_blueprint)
    api.register_blueprint(get_effects_blueprint)

    # POST
    api.register_blueprint(power_blueprint)
    api.register_blueprint(kill_blueprint)
    api.register_blueprint(dim_blueprint)
    api.register_blueprint(effect_blueprint)
    api.register_blueprint(color_blueprint)
    api.register_blueprint(mood_blueprint)
    api.register_blueprint(log_blueprint)

    TealPrint.debug("Flask API: Starting...")
    api.run(port=config.general.port)
