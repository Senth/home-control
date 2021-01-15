from flask import Flask
from ..config import config
from .light import get_lights_blueprint
from .group import get_groups_blueprint
from .kill import kill_blueprint
from .power import power_blueprint
from .dim import dim_blueprint
from .info import get_info_blueprint
from .effect import effect_blueprint, get_effects_blueprint
from .color import color_blueprint
from .mood import mood_blueprint
from .log import log_blueprint


_logger = config.logger


def run_api() -> None:
    _logger.debug("Flask API: Initializing")

    api = Flask(__package__)
    api.config["DEBUG"] = config.debug
    # FIXME different logging for --debug, --verbose, and default
    if config.debug:
        log_level = "DEBUG"
    elif config.verbose:
        log_level = "INFO"
    else:
        log_level = "WARNING"
    api.config["LOG_LEVEL"] = log_level

    _logger.debug("Flask API: Registering Blueprints")
    # Register blueprints
    # GET
    api.register_blueprint(get_lights_blueprint)
    api.register_blueprint(get_groups_blueprint)
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

    _logger.debug("Flask API: Starting...")
    api.run(port=config.webapi.port)
