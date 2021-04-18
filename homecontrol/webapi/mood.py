from typing import Any, Dict

from flask import Blueprint, abort, request

from ..smart_interfaces import SmartInterfaces
from ..smart_interfaces.moods import Mood, Moods
from . import execute, success, trim_name

mood_blueprint = Blueprint("mood", __package__)


@mood_blueprint.route("/mood", methods=["POST"])
def mood() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check required parameters
    if not "mood" in body:
        abort(400, 'Missing "mood" in body')

    if not "lights" in body:
        abort(400, 'Missing "lights" in body')

    lights = trim_name(body["lights"])
    interfaces = SmartInterfaces.get_interfaces(lights)

    mood_enum = Moods.from_name(body["mood"])
    if not mood_enum:
        abort(404, f"Didn't find a mood with the name {body['mood']}.")
    mood: Mood = mood_enum.value

    for interface in interfaces:
        execute(
            body,
            interface.color_xy,
            args=[mood.x, mood.y],
        )
        execute(
            body,
            interface.dim,
            args=[mood.brightness],
        )

    return success()