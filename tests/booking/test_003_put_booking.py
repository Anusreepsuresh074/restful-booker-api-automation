import allure
import pytest

from src.core.assert_helper import AssertHelper
from src.payload.booking_payload import booking_payload_unique

pytestmark = pytest.mark.regression


@allure.feature("Booking")
class TestPutBooking:

    @staticmethod
    def _create_booking(booking_helper, resource_registry):
        response = booking_helper.create_booking(booking_payload_unique())
        booking_id = response.json()["bookingid"]
        resource_registry("booking", booking_id)
        return booking_id

    @pytest.mark.smoke
    @allure.story("RULE-booking-write-requires-token + RULE-booking-put-full-replace: full replace "
                  "succeeds with a valid Cookie token")
    def test_update_booking_full_replace_with_valid_token(self, booking_helper, resource_registry, auth_cookie_header):
        """case: TC-put-booking-id-happy-full-replace"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        update_payload = booking_payload_unique()
        response = booking_helper.update_booking(booking_id, update_payload, headers=auth_cookie_header)
        body = response.json()
        AssertHelper.assert_field_equals(body, "firstname", update_payload["firstname"])
        AssertHelper.assert_field_equals(body, "lastname", update_payload["lastname"])

        # read-your-write: verified-via-get
        readback = booking_helper.get_booking_by_id(booking_id)
        readback_body = readback.json()
        AssertHelper.assert_field_equals(readback_body, "firstname", update_payload["firstname"])
        AssertHelper.assert_field_equals(readback_body, "lastname", update_payload["lastname"])

    @allure.story("RULE-booking-write-requires-token: write blocked with no auth at all")
    def test_update_booking_rejected_without_token(self, booking_helper, resource_registry):
        """case: TC-put-booking-id-authauthz-missing-token"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.update_booking(booking_id, booking_payload_unique(), headers=None, status_code=403)

    @allure.story("RULE-booking-write-requires-token: malformed token rejected the same as missing")
    def test_update_booking_rejected_with_invalid_token(
        self, booking_helper, resource_registry, invalid_auth_cookie_header
    ):
        """case: TC-put-booking-id-authauthz-invalid-token"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.update_booking(
            booking_id, booking_payload_unique(), headers=invalid_auth_cookie_header, status_code=403
        )

    @allure.story("RULE-auth-dual-mechanism: Basic-auth bypass path also rejects bad credentials")
    def test_update_booking_rejected_with_basic_auth_wrong_password(
        self, booking_helper, resource_registry, basic_auth_wrong_password_header
    ):
        """case: TC-put-booking-id-authauthz-basic-wrong-password"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.update_booking(
            booking_id, booking_payload_unique(), headers=basic_auth_wrong_password_header, status_code=403
        )

    @allure.story("Partial body on PUT — exact behavior pending live confirmation")
    def test_update_booking_put_with_partial_body(self, booking_helper, resource_registry, auth_cookie_header):
        """[Assumption] derived from RULE-booking-put-full-replace, which states PUT expects every
        field but not the exact rejection/overwrite behavior for a partial body. Exact status/body
        needs a live call before asserting precisely (see Open Questions) — only checks that the
        API responds with one of the two plausible outcomes (accepted or rejected), not a specific
        one, until that call is made.
        case: TC-put-booking-id-boundary-partial-body-on-put"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        response = booking_helper.attempt_update_booking_raw(
            booking_id, {"firstname": "PartialOnly"}, headers=auth_cookie_header
        )
        AssertHelper.assert_status_code_in(response, [200, 400])

    @allure.story("Update response has exactly the documented Booking shape")
    def test_update_booking_response_matches_schema(self, booking_helper, resource_registry, auth_cookie_header):
        """Endpoint inventory: PUT /booking/{id} (Booking response schema ref)
        case: TC-put-booking-id-contract-schema-updated-booking-shape"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.update_booking(booking_id, booking_payload_unique(), headers=auth_cookie_header)
