from ..tradfri.effects import Effects
from typing import Any, Dict, List
from flask import Blueprint, request, abort, jsonify
from . import success
from ..executor import EffectExecutor


effect_blueprint = Blueprint("effect", __package__)


@effect_blueprint.route("/effect", methods=["POST"])
def effect() -> str:
    body: Dict[str, Any] = request.get_json(force=True)

    # Check required parameters
    if not "name" in body:
        abort(400, 'Missing "name" field in body')

    effect = Effects.from_name(body["name"])
    if not effect:
        abort(
            404,
            f"Didn't find an effect with the name {body['name']}. see /effects for all available effects.",
        )

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