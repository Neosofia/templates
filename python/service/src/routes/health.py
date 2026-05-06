from flask import Blueprint, jsonify, Response
from core.config import settings
from core.extensions import limiter

health_bp = Blueprint("health", __name__)
policy_source = None

def init_health_routes(app, source):
    global policy_source
    policy_source = source
    app.register_blueprint(health_bp)

@health_bp.get("/health")
@limiter.limit(settings.health_rate_limit)
def health() -> Response:
    current_policy_set = policy_source.get_policy_set()
    return jsonify({"status": "ok", "version": current_policy_set["version"], "policies_dir": str(settings.authorization_policies_dir)})
