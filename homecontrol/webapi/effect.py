from homecontrol.webapi.util import get_json
from typing import List

from flask import Blueprint, abort, jsonify

from ..smart_interfaces.effects import Effects
from ..utils.executor import EffectExecutor
from . import success, trim_name

effect_blueprint = Blueprint("effect", __package__)


@effect_blueprint.route("/effect", methods=["POST"])
def effect() -> str:
    body = get_json()

    # Check required parameters
    if not "name" in body:
        abort(400, 'Missing "name" field in body')

    if not isinstance(body["name"], str):
        abort(400, '"name" field is not a string')

    name = str(trim_name(body["name"]))
    effect_enum = Effects.from_name(name)
    if not effect_enum:
        abort(
            404,
            f"Didn't find an effect with the name {body['name']}. see /effects for all available effects.",
        )
    effect = effect_enum.value

    effect_executor = EffectExecutor(effect)
    effect_executor.execute()

    return success()


get_effects_blueprint = Blueprint("get_effects", __package__)


@get_effects_blueprint.route("/effects", methods=["GET"])
def effects() -> str:
    effects: List[str] = []
    for effect in Effects:
        effects.append(effect.value.name)
    return jsonify(effects)
