from typing import Any, Callable, Dict, List

from flask import Blueprint, abort
from flask.wrappers import Response
from homecontrol.webapi.util import get_json

from ..core.entities.color import Color
from ..smart_interfaces import SmartInterfaces
from . import execute, get_delay, success, trim_name

color_blueprint = Blueprint("color", __package__)


@color_blueprint.route("/color", methods=["POST"])
def color() -> Response:
    body = get_json()

    # Check for required parameters
    if not "name" in body:
        abort(400, 'Missing "value" in body')

    name = trim_name(body["name"])
    interfaces = SmartInterfaces.get_interfaces(name)

    args: List[Any] = []
    kwargs: Dict = {}

    # TODO Fix all color parameters for /color
    # XY Color
    if "x" in body and "y" in body:
        error_msg = "xy-colors need to be floats [0.0, 1.0]"

        # Float
        if isinstance(body["x"], float) and isinstance(body["y"], float):
            if body["x"] < 0.0 or 1.0 < body["x"] or body["y"] < 0.0 or 1.0 < body["y"]:
                abort(400, error_msg)
            x = body["x"]
            y = body["y"]
            color = Color.from_xy(x, y)
            args.extend([color])

        # Not valid
        else:
            abort(400, error_msg)
    else:
        abort(400, 'Missing "x" & "y" fields')

    if "transition_time" in body:
        transition_time = get_delay(body["transition_time"])
        kwargs["transition_time"] = transition_time

    for interface in interfaces:
        execute(body, interface.color, args=args, kwargs=kwargs)

    return success()
