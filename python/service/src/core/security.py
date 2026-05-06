from functools import wraps
from typing import Callable, Any

from authentication_in_the_middle import with_authentication
from authorization_in_the_middle import with_authorization
from flask import current_app

from core.config import settings
from core.extensions import limiter
from core.logging_config import log_event
from core.auth_helpers import principal_uid, request_context

class EvaluatorProxy:
    def is_authorized(self, *args: Any, **kwargs: Any) -> bool:
        return current_app.extensions["cedar_evaluator"].is_authorized(*args, **kwargs)

evaluator_proxy = EvaluatorProxy()

def with_security(
    action: str, 
    resource_fn: Callable[[], str],
    entities_fn: Callable[[], list[dict[str, Any]]],
    rate_limit: str = "60 per minute",
) -> Callable:
    """
    Unified security decorator for Neosofia API services.
    Enforces rate limiting, JWT authentication, and Cedar authorization in one step.
    
    Args:
        action (str): The Cedar action being performed (e.g. Capabilities.DOCUMENT_READ)
        resource_fn: Callable that returns the resource uid evaluated at request-time.
        entities_fn: Callable that returns the entities payload evaluated at request-time.
        rate_limit (str): The rate limit rule to apply. Defaults to 60 per minute.
    """
    def decorator(f: Callable) -> Callable:
        # Apply decorators in reverse order (bottom-up execution):
        # 1. First rate limit
        # 2. Then authenticate JWT
        # 3. Then authorize via Cedar
        
        # Authorize
        authz_decorator = with_authorization(
            evaluator_proxy,
            principal_fn=principal_uid,
            action=action,
            resource_fn=resource_fn,
            entities_fn=entities_fn,
            context_fn=request_context,
            log_event=log_event,
        )
        
        # Authenticate
        authn_decorator = with_authentication(
            public_key=settings.jwt_public_key,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
        
        # Rate Limit
        limit_decorator = limiter.limit(rate_limit)
        
        return limit_decorator(authn_decorator(authz_decorator(f)))
    
    return decorator
