from ..tradfri.mood import Moods, Mood
from typing import Any, Dict
from flask import Blueprint, request, abort
from ..executor import DelayedExecutor
from . import get_time, success
from ..tradfri import get_light_and_groups
from ..tradfri.tradfri_gateway import TradfriGateway


mood_blueprint = Blueprint("mood", __package__)


@mood_blueprint.route("/mood", methods=["POST"])
def mood() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check required parameters
    if not "mood" in body:
        abort(400, 'Missing "mood" in body')

    if not "lights" in body:
        abort(400, 'Missing "lights" in body')

    lights_and_groups = get_light_and_groups(body["lights"])

    mood_enum = Moods.from_name(body["mood"])
    if not mood_enum:
        abort(404, f"Didn't find a mood with the name {body['mood']}.")
    mood: Mood = mood_enum.value

    delay = 0
    if "delay" in body:
        delay = get_time(body["delay"])

    # Execute immediately
    if delay == 0:
        TradfriGateway.color_xy(lights_and_groups, mood.x, mood.y)
        TradfriGateway.dim(lights_and_groups, mood.brightness)
    # Delay
    else:
        delayed_color = DelayedExecutor(
            action=TradfriGateway.color_xy,
            args=[lights_and_groups, mood.x, mood.y],
            kwargs={},
            delay=delay,
        )
        delayed_color.execute()
        delayed_brightness = DelayedExecutor(
            action=TradfriGateway.dim,
            args=[lights_and_groups, mood.brightness],
            kwargs={},
            delay=delay,
        )
        delayed_brightness.execute()

    return success()