from flask import Blueprint, jsonify
from flask.wrappers import Response

from ..data.weather import Weather

get_info_blueprint = Blueprint("get_info", __package__)


@get_info_blueprint.route("/info", methods=["GET"])
def get_info() -> Response:
    info = {
        "weather": {
            "is_raining": int(Weather.is_raining()),
            "cloud_cover": Weather.get_cloud_coverage(),
        },
    }
    return jsonify(info)
