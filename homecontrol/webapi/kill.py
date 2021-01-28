from ..executor import Executor
from . import success
from flask import Blueprint

kill_blueprint = Blueprint("kill", __package__)


@kill_blueprint.route("/kill", methods=["POST"])
def kill() -> str:
    Executor.terminate_all_running()
    return success()
