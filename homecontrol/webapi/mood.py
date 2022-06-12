from flask import Blueprint, abort
from flask.wrappers import Response
from homecontrol.webapi.util import get_json

from ..smart_interfaces import SmartInterfaces
from ..smart_interfaces.moods import Mood, Moods
from . import execute, success, trim_name

mood_blueprint = Blueprint("mood", __package__)


@mood_blueprint.route("/mood", methods=["POST"])
def mood() -> Response:
    body = get_json()

    # Check required parameters
    if "mood" not in body:
        abort(400, 'Missing "mood" in body')

    if "lights" not in body:
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
            interface.mood,
            args=[mood],
        )

    return success()
