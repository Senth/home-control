from flask import Blueprint, abort
from flask.wrappers import Response
from homecontrol.webapi.util import get_json

from ..data.stats import Stats
from . import success

log_blueprint = Blueprint("log", __package__)


@log_blueprint.route("/log", methods=["POST"])
def log() -> Response:
    body = get_json()

    # Check required parameters
    if "category" not in body:
        abort(400, 'Missing "category" field in body')

    if "value" not in body:
        abort(400, 'Missing "value" field in body')

    Stats.log(body["category"], body["value"])

    return success()
