from typing import Any, Callable
from flask import request
from authorization_in_the_middle import (
    entity_uid,
    extract_jwt_principal_entity,
    extract_jwt_principal_uid,
)
from models.document import NAMESPACE

def principal_uid() -> str:
    return extract_jwt_principal_uid(NAMESPACE)

def request_context() -> dict[str, Any]:
    return {"http_method": request.method, "route": request.url_rule.rule if request.url_rule else ""}

def request_view_arg(arg_name: str) -> str:
    return request.view_args[arg_name] if request.view_args and arg_name in request.view_args else ""

def resource_name_from_action(action: str) -> str:
    if action.startswith('Action::"') and action.endswith('"'):
        action_key = action[len('Action::"'):-1]
    else:
        action_key = action
    resource_key = action_key.split(":", 1)[0]
    return "".join(part.capitalize() for part in resource_key.replace("-", "_").split("_"))

def resource_uid_from_view_arg(
    namespace: str,
    resource_name: str,
    id_arg: str = "document_id",
    loader: Callable[[str], Any] | None = None,
) -> str:
    resource_id = request_view_arg(id_arg)
    if loader:
        loader(resource_id)
    return entity_uid(f"{namespace}::{resource_name}", resource_id)

def authorization_entities_for_resource(
    namespace: str,
    build_resource_entity: Callable[[str, dict[str, Any]], dict[str, Any]],
    resource_loader: Callable[[str], dict[str, Any]],
    id_arg: str = "document_id",
) -> list[dict[str, Any]]:
    resource_id = request_view_arg(id_arg)
    resource = resource_loader(resource_id)
    return [
        extract_jwt_principal_entity(namespace),
        build_resource_entity(resource_id, resource),
    ]
