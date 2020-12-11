from typing import List
from flask import Blueprint, jsonify
from ..tradfri.group import Groups


get_groups_blueprint = Blueprint("get_groups", __package__)


@get_groups_blueprint.route("/groups", methods=["GET"])
def lights() -> str:
    groups: List[str] = []
    for group in Groups:
        groups.append(group.value)
    return jsonify(groups)