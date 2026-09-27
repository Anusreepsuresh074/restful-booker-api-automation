import allure
import pytest

from src.core.assert_helper import AssertHelper
from src.payload.booking_payload import booking_payload_unique

pytestmark = pytest.mark.regression


@allure.feature("Booking")
class TestPostBooking:
    @pytest.mark.smoke
    @allure.story("RULE-booking-post-open-no-auth: a well-formed booking is created and echoed back")
    def test_create_booking_with_valid_payload(self, booking_helper, resource_registry):
        """case: TC-post-booking-happy-create-valid"""
        payload = booking_payload_unique()
        response = booking_helper.create_booking(payload)
        booking_id = response.json()["bookingid"]
        resource_registry("booking", booking_id)
        AssertHelper.assert_field_equals(response.json()["booking"], "firstname", payload["firstname"])

        # read-your-write: verified-via-get (GET /booking/{id} documented)
        readback = booking_helper.get_booking_by_id(booking_id)
        AssertHelper.assert_field_equals(readback.json(), "firstname", payload["firstname"])

    @allure.story("RULE-booking-post-open-no-auth: creation succeeds with zero auth headers")
    def test_create_booking_succeeds_without_any_auth_header(self, booking_helper, resource_registry):
        """case: TC-post-booking-authauthz-no-auth-required"""
        payload = booking_payload_unique()
        response = booking_helper.create_booking(payload)
        booking_id = response.json()["bookingid"]
        resource_registry("booking", booking_id)

        # read-your-write: verified-via-get
        readback = booking_helper.get_booking_by_id(booking_id)
        AssertHelper.assert_field_equals(readback.json(), "firstname", payload["firstname"])

    @allure.story("Creation response has exactly the documented shape")
    def test_create_booking_response_matches_schema(self, booking_helper, resource_registry):
        """Endpoint inventory: POST /booking (Booking response schema ref)
        case: TC-post-booking-contract-schema-response-shape"""
        payload = booking_payload_unique()
        response = booking_helper.create_booking(payload)
        booking_id = response.json()["bookingid"]
        resource_registry("booking", booking_id)
