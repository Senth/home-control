from ..executor import DelayedExecutor
from typing import Any, Dict, Union
from ..tradfri import get_light_and_groups
from ..tradfri.tradfri_gateway import TradfriGateway
from . import success, get_time
from flask import Blueprint, request, abort


dim_blueprint = Blueprint("dim", __package__)


@dim_blueprint.route("/dim", methods=["POST"])
def dim() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check required parameters
    if not "value" in body:
        abort(400, 'Missing "value" in body')

    if not "name" in body:
        abort(400, 'Missing "name" in body')

    lights_and_groups = get_light_and_groups(body["name"])

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
        transition_time = get_time(body["transition_time"])

    # Delay
    delay = 0
    if "delay" in body:
        delay = get_time(body["delay"])

    # Execute directly
    if delay == 0:
        TradfriGateway.dim(lights_and_groups, value, transition_time)
    # Delayed
    else:
        delayed_executor = DelayedExecutor(
            action=TradfriGateway.dim,
            args=[lights_and_groups, value],
            kwargs={"transition_time": transition_time},
            delay=delay,
        )
        delayed_executor.execute()

    return success()