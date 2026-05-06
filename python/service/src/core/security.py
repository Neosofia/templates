from functools import wraps
from typing import Callable, Any

from authentication_in_the_middle import with_authentication
from authorization_in_the_middle import with_authorization
from flask import current_app, request

from core.config import settings
from core.extensions import limiter
from core.logging_config import log_event
from core.auth_helpers import (
    principal_uid,
    request_context,
    resource_name_from_action,
    resource_uid_from_view_arg,
    authorization_entities_for_resource,
)

class EvaluatorProxy:
    def is_authorized(self, *args: Any, **kwargs: Any) -> bool:
        return current_app.extensions["cedar_evaluator"].is_authorized(*args, **kwargs)

evaluator_proxy = EvaluatorProxy()

def with_security(
    action: str,
    resource_fn: Callable[[], str] | None = None,
    entities_fn: Callable[[], list[dict[str, Any]]] | None = None,
    namespace: str | None = None,
    build_resource_entity: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
    resource_loader: Callable[[str], dict[str, Any]] | None = None,
    id_arg: str | None = None,
    rate_limit: str = "60 per minute",
) -> Callable:
    """
    Unified security decorator for Neosofia API services.
    Enforces rate limiting, JWT authentication, and Cedar authorization in one step.
    """
    def decorator(f: Callable) -> Callable:
        import importlib
        
        # Apply decorators in reverse order (bottom-up execution):
        # 1. First rate limit
        # 2. Then authenticate JWT
        # 3. Then authorize via Cedar

        resource_fn_local = resource_fn
        entities_fn_local = entities_fn
        
        action_key = action[len('Action::"'):-1] if action.startswith('Action::"') else action
        model_name = action_key.split(":", 1)[0].replace("-", "_").lower()
        target_id_arg = id_arg or f"{model_name}_id"
        resolved_resource_name = "".join(part.capitalize() for part in model_name.split("_"))

        if resource_fn_local is None or entities_fn_local is None:
            # Try to infer missing namespace, loader, or builder by convention
            resource_name = resolved_resource_name
            
            inferred_namespace = namespace
            inferred_loader = resource_loader
            inferred_builder = build_resource_entity
            
            if inferred_namespace is None or inferred_builder is None or inferred_loader is None:
                try:
                    if inferred_loader is None:
                        service_mod = importlib.import_module(f"services.{model_name}_service")
                        inferred_loader = getattr(service_mod, f"get_{model_name}_or_404")
                    
                    if inferred_builder is None or inferred_namespace is None:
                        model_mod = importlib.import_module(f"models.{model_name}")
                        if inferred_builder is None:
                            inferred_builder = getattr(model_mod, f"build_{model_name}_entity")
                        if inferred_namespace is None:
                            inferred_namespace = getattr(model_mod, "NAMESPACE")
                except (ImportError, AttributeError) as e:
                    raise ValueError(
                        f"Could not infer authorization helpers for '{model_name}'. "
                        f"Please provide namespace, resource_loader, and build_resource_entity explicitly. Error: {e}"
                    )
            
            if resource_fn_local is None:
                resource_fn_local = lambda: resource_uid_from_view_arg(
                    inferred_namespace,
                    resource_name,
                    id_arg=target_id_arg,
                    loader=inferred_loader,
                )
            if entities_fn_local is None:
                entities_fn_local = lambda: authorization_entities_for_resource(
                    inferred_namespace,
                    inferred_builder,
                    inferred_loader,
                    id_arg=target_id_arg,
                )

        # Authorize
        authz_decorator = with_authorization(
            evaluator_proxy,
            principal_fn=principal_uid,
            action=action,
            resource_fn=resource_fn_local,
            entities_fn=entities_fn_local,
            context_fn=request_context,
            log_event=log_event,
        )
        
        # Authenticate
        authn_decorator = with_authentication(
            public_key=settings.jwt_public_key,
            jwks_uri=getattr(settings, "jwt_jwks_uri", None),
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
        
        # Rate Limit
        limit_decorator = limiter.limit(rate_limit)

        @wraps(f)
        def pre_authz_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Authn has succeeded by here, so we can safely extract the principal.
            try:
                p_uid = principal_uid()
            except Exception:
                p_uid = "unknown"

            trace_id = request.headers.get("traceparent") or request.headers.get("X-Transaction-Id")
            
            log_kwargs = {
                "route": f.__name__,
                "principal": p_uid,
                "action": action,
                "resource_name": resolved_resource_name,
                "resource_id": kwargs.get(target_id_arg),
                "rate_limit": rate_limit,
                "authn_issuer": settings.jwt_issuer,
                "authn_audience": settings.jwt_audience,
            }
            if trace_id:
                log_kwargs["trace_id"] = trace_id

            log_event("security_evaluation_started", **log_kwargs)
            return authz_decorator(f)(*args, **kwargs)

        return limit_decorator(authn_decorator(pre_authz_wrapper))
    
    return decorator
