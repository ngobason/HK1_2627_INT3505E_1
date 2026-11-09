from flask import Blueprint, jsonify
from sqlalchemy import text
from ..extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200


@health_bp.get("/ready")
def readiness():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ok",
            "checks": {"db": "ok"}
        }), 200
    except Exception:
        return jsonify({
            "status": "degraded",
            "checks": {"db": "err"}
        }), 503