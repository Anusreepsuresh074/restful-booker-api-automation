import allure
import pytest

from src.core.assert_helper import AssertHelper

pytestmark = pytest.mark.regression


@allure.feature("Ping")
class TestPingHealthCheck:

    @pytest.mark.smoke
    @allure.story("RULE-ping-health-check: GET /ping returns 201 Created with body 'Created'")
    def test_ping_returns_health_check(self, ping_helper):
        """case: TC-get-ping-happy-returns-201"""
        response = ping_helper.ping()
        AssertHelper.assert_status_code(response, 201)
        AssertHelper.assert_equals(response.text, "Created", context="ping body ")

    @allure.story("Ping body is a literal string, not a JSON structure")
    def test_ping_response_is_plain_text_not_json(self, ping_helper):
        """case: TC-get-ping-contract-schema-plain-text-body"""
        response = ping_helper.ping()
        AssertHelper.assert_equals(response.text, "Created", context="ping body ")
        with pytest.raises(ValueError):
            response.json()
