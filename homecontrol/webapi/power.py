from typing import Any, Dict
from . import success, execute
from ..tradfri import get_light_and_groups
from ..tradfri.tradfri_gateway import TradfriGateway
from flask import Blueprint, request, abort

power_blueprint = Blueprint("power", __package__)


@power_blueprint.route("/power", methods=["POST"])
def power() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check required parameters
    if not "value" in body:
        abort(400, 'Missing "value" in body')

    if not "name" in body:
        abort(400, 'Missing "name" in body')

    lights_and_groups = get_light_and_groups(body["name"])

    if isinstance(body["value"], str):
        body["value"] = str(body["value"]).lower()

    if body["value"] == "on" or body["value"] == 1:
        action = TradfriGateway.turn_on
    elif body["value"] == "off" or body["value"] == 0:
        action = TradfriGateway.turn_off
    elif body["value"] == "toggle":
        action = TradfriGateway.toggle
    else:
        abort(
            400,
            'field "value" has invalid value. Valid values are: "on"/"off"/1/0/"toggle"',
        )

    execute(body, action, args=[lights_and_groups])

    return success()