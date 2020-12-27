from typing import Any, Callable, Dict, List
from flask import Blueprint, request, abort
from . import execute, success, get_delay
from ..tradfri import get_light_and_groups
from ..tradfri.tradfri_gateway import TradfriGateway

color_blueprint = Blueprint("color", __package__)

MAX_COLOR_INT = 65535


@color_blueprint.route("/color", methods=["POST"])
def color() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check for required parameters
    if not "name" in body:
        abort(400, 'Missing "value" in body')

    lights_and_groups = get_light_and_groups(body["name"])

    action: Callable
    args: List[Any] = [lights_and_groups]
    kwargs: Dict = {}

    # Hex
    if "color" in body:
        action = TradfriGateway.color_hex
        args.append(body["color"])
    # XY Color
    elif "x" in body and "y" in body:
        error_msg = "xy-colors need to be integers [0, 65535] or floats [0.0, 1.0]"

        # Int
        if isinstance(body["x"], int) and isinstance(body["y"], int):
            if (
                body["x"] < 0
                or MAX_COLOR_INT < body["x"]
                or body["y"] < 0
                or MAX_COLOR_INT < body["y"]
            ):
                abort(400, error_msg)
            action = TradfriGateway.color_xy
            args.extend([body["x"], body["y"]])

        # Float -> Normalize to 0-65535
        elif isinstance(body["x"], float) and isinstance(body["y"], float):
            if body["x"] < 0.0 or 1.0 < body["x"] or body["y"] < 0.0 or 1.0 < body["y"]:
                abort(400, error_msg)
            x = int(body["x"] * MAX_COLOR_INT)
            y = int(body["y"] * MAX_COLOR_INT)
            action = TradfriGateway.color_xy
            args.extend([x, y])

        # Not valid
        else:
            abort(400, error_msg)
    else:
        abort(400, 'Missing "color" or "x"/"y" field')

    if "transition_time" in body:
        transition_time = get_delay(body["transition_time"])
        kwargs["transition_time"] = transition_time

    execute(body, action, args=args, kwargs=kwargs)

    return success()