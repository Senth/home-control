from flask import Blueprint, jsonify
from flask.wrappers import Response

from ..data.network import Network
from ..data.network.guest_of import GuestOf
from ..data.weather import Weather
from ..smart_interfaces.sensors import Sensors

get_info_blueprint = Blueprint("get_info", __package__)


@get_info_blueprint.route("/info", methods=["GET"])
def get_info() -> Response:
    info = {
        "weather": {
            "is_raining": int(Weather.is_raining()),
            "cloud_cover": Weather.get_cloud_coverage(),
        },
        "sensor": {
            "living_room": Sensors.livingroom_light.get_light_name_from_level().name,
            "kitchen": Sensors.kitchen_light.get_light_name_from_level().name,
        },
        "network": {
            "guests": {
                "any": Network.is_guest_home(),
                "both": Network.is_guest_home(GuestOf.both),
                "emma": Network.is_guest_home(GuestOf.emma),
                "matteus": Network.is_guest_home(GuestOf.matteus),
            },
            "devices": {
                "zen": Network.zen.is_on(),
                "work_matteus": Network.work_matteus.is_on(),
                "tv": Network.tv.is_on(),
                "mobile_matteus": Network.mobile_matteus.is_on(),
                "mobile_emma": Network.mobile_emma.is_on(),
            },
        },
    }
    return jsonify(info)
