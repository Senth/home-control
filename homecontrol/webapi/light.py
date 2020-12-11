from typing import List
from flask import Blueprint, jsonify
from ..tradfri.light import Lights


get_lights_blueprint = Blueprint("get_lights", __package__)


@get_lights_blueprint.route("/lights", methods=["GET"])
def lights() -> str:
    lights: List[str] = []
    for light in Lights:
        lights.append(light.value)
    return jsonify(lights)