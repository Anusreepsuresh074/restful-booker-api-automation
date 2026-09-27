import allure
import pytest

from src.core.assert_helper import AssertHelper
from src.payload.booking_payload import booking_partial_update_payload, booking_payload_unique

pytestmark = pytest.mark.regression


@allure.feature("Booking")
class TestPatchBooking:

    @staticmethod
    def _create_booking(booking_helper, resource_registry):
        original_payload = booking_payload_unique()
        response = booking_helper.create_booking(original_payload)
        booking_id = response.json()["bookingid"]
        resource_registry("booking", booking_id)
        return booking_id, original_payload

    @pytest.mark.smoke
    @allure.story("RULE-booking-write-requires-token: partial update changes only the sent fields")
    def test_partial_update_booking_with_valid_token(self, booking_helper, resource_registry, auth_cookie_header):
        """case: TC-patch-booking-id-happy-partial-update"""
        booking_id, original_payload = self._create_booking(booking_helper, resource_registry)
        patch_payload = booking_partial_update_payload()
        response = booking_helper.partial_update_booking(booking_id, patch_payload, headers=auth_cookie_header)
        body = response.json()
        AssertHelper.assert_field_equals(body, "firstname", patch_payload["firstname"])
        AssertHelper.assert_field_equals(body, "lastname", original_payload["lastname"])

        # read-your-write: verified-via-get
        readback = booking_helper.get_booking_by_id(booking_id)
        readback_body = readback.json()
        AssertHelper.assert_field_equals(readback_body, "firstname", patch_payload["firstname"])
        AssertHelper.assert_field_equals(readback_body, "lastname", original_payload["lastname"])

    @allure.story("RULE-booking-write-requires-token: PATCH enforces the same auth requirement as PUT")
    def test_partial_update_booking_rejected_without_token(self, booking_helper, resource_registry):
        """case: TC-patch-booking-id-authauthz-missing-token"""
        booking_id, _ = self._create_booking(booking_helper, resource_registry)
        booking_helper.partial_update_booking(
            booking_id, booking_partial_update_payload(), headers=None, status_code=403
        )

    @allure.story("RULE-booking-write-requires-token: malformed token rejected on PATCH too")
    def test_partial_update_booking_rejected_with_invalid_token(
        self, booking_helper, resource_registry, invalid_auth_cookie_header
    ):
        """case: TC-patch-booking-id-authauthz-invalid-token"""
        booking_id, _ = self._create_booking(booking_helper, resource_registry)
        booking_helper.partial_update_booking(
            booking_id, booking_partial_update_payload(), headers=invalid_auth_cookie_header, status_code=403
        )

    @allure.story("Partial-update response has exactly the documented Booking shape")
    def test_partial_update_booking_response_matches_schema(
        self, booking_helper, resource_registry, auth_cookie_header
    ):
        """Endpoint inventory: PATCH /booking/{id} (Booking response schema ref)
        case: TC-patch-booking-id-contract-schema-updated-booking-shape"""
        booking_id, _ = self._create_booking(booking_helper, resource_registry)
        booking_helper.partial_update_booking(
            booking_id, booking_partial_update_payload(), headers=auth_cookie_header
        )
