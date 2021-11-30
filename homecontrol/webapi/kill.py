from flask import Blueprint
from flask.wrappers import Response

from ..utils.executor import Executor
from . import success

kill_blueprint = Blueprint("kill", __package__)


@kill_blueprint.route("/kill", methods=["POST"])
def kill() -> Response:
    Executor.terminate_all_running()
    return success()
