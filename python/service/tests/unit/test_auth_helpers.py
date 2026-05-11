import pytest
from flask import g
from werkzeug.exceptions import BadRequest, Forbidden

from src.bootstrap.auth_helpers import get_validated_principal, resource_name_from_action

pytestmark = pytest.mark.unit


class TestResourceNameFromAction:
    def test_with_cedar_action_prefix(self):
        assert resource_name_from_action('Action::"document:read"') == "Document"

    def test_without_cedar_action_prefix(self):
        assert resource_name_from_action("document:read") == "Document"

    def test_multi_word_resource(self):
        assert resource_name_from_action('Action::"medical_record:read"') == "MedicalRecord"


class TestGetValidatedPrincipal:
    def _claims(self, **extra):
        return {"sub": "u1", "neosofia:principal_type": "Patient", **extra}

    def test_non_list_roles_treated_as_empty(self, app):
        with app.test_request_context("/api/v1/documents/d1"):
            g.jwt_claims = self._claims(**{"neosofia:roles": "not-a-list"})
            entity = get_validated_principal("neosofia")
            # line 24: auth_roles reset to []; 0 roles → no error
            assert entity is not None

    def test_invalid_role_format_raises_bad_request(self, app):
        with app.test_request_context("/api/v1/documents/d1", headers={"X-Active-Role": "invalid role!"}):
            g.jwt_claims = self._claims()
            with pytest.raises(BadRequest):
                get_validated_principal("neosofia")

    def test_unauthorized_role_raises_forbidden(self, app):
        with app.test_request_context("/api/v1/documents/d1", headers={"X-Active-Role": "admin"}):
            g.jwt_claims = self._claims()  # no roles claim → auth_roles = []
            with pytest.raises(Forbidden):
                get_validated_principal("neosofia")

    def test_valid_active_role_filters_to_single(self, app):
        with app.test_request_context("/api/v1/documents/d1", headers={"X-Active-Role": "physician"}):
            g.jwt_claims = self._claims(**{"neosofia:roles": ["physician", "admin"]})
            entity = get_validated_principal("neosofia")
            assert entity["attrs"]["roles"] == ["physician"]

    def test_multiple_roles_without_header_raises_bad_request(self, app):
        with app.test_request_context("/api/v1/documents/d1"):
            g.jwt_claims = self._claims(**{"neosofia:roles": ["physician", "admin"]})
            with pytest.raises(BadRequest):
                get_validated_principal("neosofia")
