from typing import Union

from flask import Blueprint, abort
from flask.wrappers import Response
from homecontrol.webapi.util import get_json

from ..smart_interfaces import SmartInterfaces
from . import execute, get_delay, success, trim_name

dim_blueprint = Blueprint("dim", __package__)


@dim_blueprint.route("/dim", methods=["POST"])
def dim() -> Response:
    body = get_json()

    # Check required parameters
    if "value" not in body:
        abort(400, 'Missing "value" in body')

    if "name" not in body:
        abort(400, 'Missing "name" in body')

    name = trim_name(body["name"])
    interfaces = SmartInterfaces.get_interfaces(name)

    # Value
    value: Union[float, int] = 0
    if isinstance(body["value"], int):
        value = int(body["value"])

        if value < 0 or 254 < value:
            abort(400, "The value needs to be in the range of [0, 254] for integers")
    elif isinstance(body["value"], float):
        value = float(body["value"])

        if value < 0.0 or 1.0 < value:
            abort(400, "The value needs to be in the rang of [0.0, 1.0] for floats")
    else:
        abort(400, 'Field "value" needs to be an integer [0, 254] or float [0.0, 1.0].')

    # Transition Time
    transition_time = 1.0
    if "transition_time" in body:
        transition_time = get_delay(body["transition_time"])

    for interface in interfaces:
        execute(
            body,
            interface.dim,
            args=[value],
            kwargs={"transition_time": transition_time},
        )

    return success()
