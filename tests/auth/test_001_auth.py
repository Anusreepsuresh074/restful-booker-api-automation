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
        """Observed live (context/schema-validation-report.md row 6, context/api-auth.md): this API
        answers bad credentials with `200 OK` and `{"reason": "Bad credentials"}`, not a 4xx.
        case: TC-post-auth-negative-wrong-credentials"""
        response = auth_helper.authenticate_raw(auth_payload_wrong_credentials())
        AssertHelper.assert_status_code(response, 200)
        body = response.json()
        AssertHelper.assert_field_absent(body, "token")
        AssertHelper.assert_equals(body, {"reason": "Bad credentials"}, context="auth failure body ")

    @allure.story("Missing password field is rejected")
    def test_auth_rejects_missing_password_field(self, auth_helper):
        """[Assumption] both fields are stated required but no documented rejection behavior
        exists. Observed live (context/schema-validation-report.md row 7): a missing `password` is
        treated exactly like wrong credentials — `200 OK` and `{"reason": "Bad credentials"}`.
        case: TC-post-auth-boundary-missing-password-field"""
        response = auth_helper.authenticate_raw(auth_payload_missing_password())
        AssertHelper.assert_status_code(response, 200)
        body = response.json()
        AssertHelper.assert_field_absent(body, "token")
        AssertHelper.assert_equals(body, {"reason": "Bad credentials"}, context="auth failure body ")

    @allure.story("Success response has exactly the documented token shape")
    def test_auth_response_matches_token_schema(self, auth_helper):
        """Endpoint inventory: POST /auth (AuthToken response schema ref)
        case: TC-post-auth-contract-schema-token-response"""
        response = auth_helper.authenticate()
        AssertHelper.assert_schema(response.json(), AUTH_TOKEN_SCHEMA)
