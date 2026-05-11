from typing import Any
from flask import Blueprint, jsonify, Response
from src.bootstrap.capabilities import Capabilities
from src.bootstrap.config import settings
from src.services.document_service import get_document_or_404
from src.models.document import build_document_entity, NAMESPACE
from src.bootstrap.security import with_security

docs_bp = Blueprint("documents", __name__, url_prefix="/api/v1/documents")

def init_docs_routes(app, cedar_evaluator):
    app.extensions["cedar_evaluator"] = cedar_evaluator
    app.register_blueprint(docs_bp)

@docs_bp.get("/<document_id>")
@with_security(
    action=Capabilities.DOCUMENT_READ,
    rate_limit=settings.document_read_rate_limit,
)
def get_document(document_id: str) -> Response:
    document = get_document_or_404(document_id)
    return jsonify({"document_id": document_id, "title": document["title"], "clinic_id": document["clinic_id"]})

@docs_bp.get("/<document_id>/summary")
@with_security(
    action=Capabilities.DOCUMENT_READ,
    rate_limit=settings.document_read_rate_limit,
)
def get_document_summary(document_id: str) -> Response:
    document = get_document_or_404(document_id)
    return jsonify({"document_id": document_id, "summary": document["summary"]})

@docs_bp.delete("/<document_id>")
@with_security(
    action=Capabilities.DOCUMENT_DELETE,
    rate_limit=settings.document_delete_rate_limit,
)
def delete_document(document_id: str) -> Response:
    get_document_or_404(document_id)
    return jsonify({"deleted": document_id})
