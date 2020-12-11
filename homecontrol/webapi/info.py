from flask import jsonify, Blueprint
from ..info_wrapper import InfoWrapper

get_info_blueprint = Blueprint("get_info", __package__)


@get_info_blueprint.route("/info", methods=["GET"])
def get_info() -> str:
    return jsonify(InfoWrapper.get_day_info())