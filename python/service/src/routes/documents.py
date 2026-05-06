from typing import Any
from flask import Blueprint, jsonify, Response, request
from authorization_in_the_middle import entity_uid, extract_jwt_principal_entity
from core.capabilities import Capabilities
from core.config import settings
from services.document_service import get_document_or_404
from models.document import build_document_entity, NAMESPACE
from core.security import with_security, evaluator_proxy

docs_bp = Blueprint("documents", __name__, url_prefix="/api/v1/documents")

def document_resource_uid() -> str:
    document_id = request.view_args["document_id"] if request.view_args else ""
    get_document_or_404(document_id)
    return entity_uid(f"{NAMESPACE}::Document", document_id)

def document_authorization_entities() -> list[dict[str, Any]]:
    document_id = request.view_args["document_id"] if request.view_args else ""
    document = get_document_or_404(document_id)
    return [
        extract_jwt_principal_entity(NAMESPACE),
        build_document_entity(document_id, document),
    ]

def init_docs_routes(app, cedar_evaluator):
    app.extensions["cedar_evaluator"] = cedar_evaluator
    app.register_blueprint(docs_bp)

@docs_bp.get("/<document_id>")
@with_security(
    action=Capabilities.DOCUMENT_READ,
    resource_fn=document_resource_uid,
    entities_fn=document_authorization_entities,
    rate_limit=settings.document_read_rate_limit,
)
def get_document(document_id: str) -> Response:
    document = get_document_or_404(document_id)
    return jsonify({"document_id": document_id, "title": document["title"], "clinic_id": document["clinic_id"]})

@docs_bp.get("/<document_id>/summary")
@with_security(
    action=Capabilities.DOCUMENT_READ,
    resource_fn=document_resource_uid,
    entities_fn=document_authorization_entities,
    rate_limit=settings.document_read_rate_limit,
)
def get_document_summary(document_id: str) -> Response:
    document = get_document_or_404(document_id)
    return jsonify({"document_id": document_id, "summary": document["summary"]})

@docs_bp.delete("/<document_id>")
@with_security(
    action=Capabilities.DOCUMENT_DELETE,
    resource_fn=document_resource_uid,
    entities_fn=document_authorization_entities,
    rate_limit=settings.document_delete_rate_limit,
)
def delete_document(document_id: str) -> Response:
    get_document_or_404(document_id)
    return jsonify({"deleted": document_id})
