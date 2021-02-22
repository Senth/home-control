from flask import jsonify, Blueprint
from ..data.luminance import Luminance
from ..data.weather import Weather

get_info_blueprint = Blueprint("get_info", __package__)


@get_info_blueprint.route("/info", methods=["GET"])
def get_info() -> str:
    info = {
        "luminance": {"is_dark": int(Luminance.is_dark())},
        "sun": {
            "is_up": int(not Luminance.is_sun_down()),
        },
        "weather": {
            "is_raining": int(Weather.is_raining()),
            "cloud_cover": Weather.get_cloud_coverage(),
        },
    }
    return jsonify(info)