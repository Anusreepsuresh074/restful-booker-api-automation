import allure
import pytest

from src.core.assert_helper import AssertHelper
from src.payload.auth_payload import auth_payload_missing_password, auth_payload_wrong_credentials
from src.schema.auth_schema import AUTH_TOKEN_SCHEMA

pytestmark = pytest.mark.regression


@allure.feature("Auth")
class TestAuth:
    @pytest.mark.smoke
    @allure.story("Valid documented credentials exchange for a token")
    def test_auth_returns_token_for_valid_credentials(self, auth_helper):
        """Endpoint inventory: POST /auth (AuthToken response schema ref)
        case: TC-post-auth-happy-valid-credentials"""
        response = auth_helper.authenticate()
        body = response.json()
        AssertHelper.assert_field_present(body, "token")
        AssertHelper.assert_is_instance(body["token"], str, context="token")

    @allure.story("Wrong credentials do not mint a token")
    def test_auth_rejects_wrong_credentials(self, auth_helper):
        """context/api-auth.md Open Questions: exact response for bad /auth credentials is
        unconfirmed — do not assume 403 or 200-with-error. Asserts only that wrong credentials
        never yield a usable token; tighten to an exact status once a live call confirms it.
        case: TC-post-auth-negative-wrong-credentials"""
        response = auth_helper.authenticate_raw(auth_payload_wrong_credentials())
        if response.status_code == 200:
            body = response.json()
            assert not body.get("token"), f"Wrong credentials must not yield a usable token. Body: {body}"
        else:
            AssertHelper.assert_status_code_in(response, [400, 401, 403])

    @allure.story("Missing password field is rejected")
    def test_auth_rejects_missing_password_field(self, auth_helper):
        """[Assumption] both fields are stated required but no documented rejection behavior
        exists — same unconfirmed-status handling as the wrong-credentials case above.
        case: TC-post-auth-boundary-missing-password-field"""
        response = auth_helper.authenticate_raw(auth_payload_missing_password())
        if response.status_code == 200:
            body = response.json()
            assert not body.get("token"), f"Missing password must not yield a usable token. Body: {body}"
        else:
            AssertHelper.assert_status_code_in(response, [400, 401, 403])

    @allure.story("Success response has exactly the documented token shape")
    def test_auth_response_matches_token_schema(self, auth_helper):
        """Endpoint inventory: POST /auth (AuthToken response schema ref)
        case: TC-post-auth-contract-schema-token-response"""
        response = auth_helper.authenticate()
        AssertHelper.assert_schema(response.json(), AUTH_TOKEN_SCHEMA)
