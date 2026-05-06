from typing import Any
from flask import request
from authorization_in_the_middle import extract_jwt_principal_uid
from models.document import NAMESPACE

def principal_uid() -> str:
    return extract_jwt_principal_uid(NAMESPACE)

def request_context() -> dict[str, Any]:
    return {"http_method": request.method, "route": request.url_rule.rule if request.url_rule else ""}
