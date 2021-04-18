from typing import Any, Dict

from flask import Blueprint, abort, request

from ..data.stats import Stats
from . import success

log_blueprint = Blueprint("log", __package__)


@log_blueprint.route("/log", methods=["POST"])
def log() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check required parameters
    if not "category" in body:
        abort(400, 'Missing "category" field in body')

    if not "value" in body:
        abort(400, 'Missing "value" field in body')

    Stats.log(body["category"], body["value"])

    return success()