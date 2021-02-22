from typing import Any, Dict
from . import success, execute, trim_name
from ..smart_interfaces import SmartInterfaces
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

    name = trim_name(body["name"])
    interfaces = SmartInterfaces.get_interfaces(name)

    if isinstance(body["value"], str):
        body["value"] = str(body["value"]).lower()

    for interface in interfaces:
        if body["value"] == "on" or body["value"] == 1:
            action = interface.turn_on
        elif body["value"] == "off" or body["value"] == 0:
            action = interface.turn_off
        elif body["value"] == "toggle":
            action = interface.toggle
        else:
            abort(
                400,
                'field "value" has invalid value. Valid values are: "on"/"off"/1/0/"toggle"',
            )

        execute(body, action)

    return success()