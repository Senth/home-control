from ..tradfri.mood import Moods, Mood
from typing import Any, Dict
from flask import Blueprint, request, abort
from . import execute, success
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

    execute(
        body,
        TradfriGateway.color_xy,
        args=[lights_and_groups, mood.x, mood.y],
    )
    execute(
        body,
        TradfriGateway.dim,
        args=[lights_and_groups, mood.brightness],
    )

    return success()