import allure
import pytest

from src.payload.booking_payload import booking_payload_unique

pytestmark = pytest.mark.regression


@allure.feature("Booking")
class TestDeleteBooking:
    @staticmethod
    def _create_booking(booking_helper, resource_registry):
        response = booking_helper.create_booking(booking_payload_unique())
        booking_id = response.json()["bookingid"]
        resource_registry("booking", booking_id)
        return booking_id

    @pytest.mark.smoke
    @allure.story("RULE-booking-delete-status-201: successful delete returns the API's non-standard 201")
    def test_delete_booking_with_valid_token_returns_201(self, booking_helper, resource_registry, auth_cookie_header):
        """case: TC-delete-booking-id-happy-valid-token-returns-201"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.delete_booking(booking_id, headers=auth_cookie_header, status_code=201)

        # read-your-write: verified-via-get; no documented soft-delete field for this API,
        # so removal is verified via 404 on the follow-up GET (Step 6.5 default).
        booking_helper.get_booking_by_id(booking_id, status_code=404)

    @allure.story("RULE-booking-write-requires-token: delete blocked with no auth at all")
    def test_delete_booking_rejected_without_token(self, booking_helper, resource_registry):
        """case: TC-delete-booking-id-authauthz-missing-token"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.delete_booking(booking_id, headers=None, status_code=403)

    @allure.story("RULE-booking-write-requires-token: malformed token rejected on delete too")
    def test_delete_booking_rejected_with_invalid_token(
        self, booking_helper, resource_registry, invalid_auth_cookie_header
    ):
        """case: TC-delete-booking-id-authauthz-invalid-token"""
        booking_id = self._create_booking(booking_helper, resource_registry)
        booking_helper.delete_booking(booking_id, headers=invalid_auth_cookie_header, status_code=403)
