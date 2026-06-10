from flask import Blueprint, jsonify, Response
from src.bootstrap.config import settings
from src.services.document_service import get_document_or_404
from authorization_in_the_middle.security import with_security

docs_bp = Blueprint("documents", __name__, url_prefix="/api/v1/documents")

def init_docs_routes(app, cedar_evaluator):
    app.extensions["cedar_evaluator"] = cedar_evaluator
    app.register_blueprint(docs_bp)

@docs_bp.get("/<document_id>")
@with_security(rate_limit=settings.document_read_rate_limit, resource_loader=get_document_or_404)
def get_document(document_id: str) -> Response:
    document = get_document_or_404(document_id)
    return jsonify({"document_id": document_id, "title": document["title"], "clinic_id": document["clinic_id"]})

@docs_bp.get("/<document_id>/summary")
@with_security(rate_limit=settings.document_read_rate_limit, resource_loader=get_document_or_404)
def get_document_summary(document_id: str) -> Response:
    document = get_document_or_404(document_id)
    return jsonify({"document_id": document_id, "summary": document["summary"]})

@docs_bp.delete("/<document_id>")
@with_security(rate_limit=settings.document_delete_rate_limit, resource_loader=get_document_or_404)
def delete_document(document_id: str) -> Response:
    get_document_or_404(document_id)
    return jsonify({"deleted": document_id})
