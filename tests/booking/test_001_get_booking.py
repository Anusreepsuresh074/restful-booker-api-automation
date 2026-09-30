import uuid

import allure
import pytest

from src.core.assert_helper import AssertHelper
from src.payload.booking_payload import booking_payload_unique

pytestmark = pytest.mark.regression


@allure.feature("Booking")
class TestGetBooking:
    @pytest.mark.smoke
    @allure.story("RULE-data-shared-instance: filtering finds the test's own booking by id")
    def test_get_booking_filter_returns_own_created_id(self, booking_helper, resource_registry):
        """case: TC-get-booking-happy-filter-returns-created-id"""
        payload = booking_payload_unique()
        create_response = booking_helper.create_booking(payload)
        booking_id = create_response.json()["bookingid"]
        resource_registry("booking", booking_id)

        filter_response = booking_helper.list_bookings(
            params={"firstname": payload["firstname"], "lastname": payload["lastname"]}
        )
        returned_ids = [item["bookingid"] for item in filter_response.json()]
        AssertHelper.assert_contains(returned_ids, booking_id, context="filtered booking ids ")

    @pytest.mark.smoke
    @allure.story("Unfiltered list endpoint responds correctly")
    def test_get_booking_list_no_filters(self, booking_helper):
        """Endpoint inventory: GET /booking (BookingIdList response schema ref)
        case: TC-get-booking-happy-list-all"""
        booking_helper.list_bookings()

    @allure.story("A filter matching nothing degrades gracefully instead of erroring")
    def test_get_booking_filter_no_matches_returns_empty(self, booking_helper):
        """[Assumption] empty-result behavior isn't explicitly documented — matrix's own inferred
        expectation (200 + empty array), confirmed live (context/schema-validation-report.md row 10).
        case: TC-get-booking-boundary-filter-no-matches"""
        no_match_name = f"NoMatch{uuid.uuid4().hex}"
        response = booking_helper.list_bookings(params={"firstname": no_match_name})
        AssertHelper.assert_equals(response.json(), [], context="filtered booking list ")

    @pytest.mark.smoke
    @allure.story("A booking created by the test can be read back exactly")
    def test_get_booking_by_id_returns_full_record(self, booking_helper, resource_registry):
        """Endpoint inventory: GET /booking/{id} (Booking response schema ref)
        case: TC-get-booking-id-happy-fetch-existing"""
        payload = booking_payload_unique()
        create_response = booking_helper.create_booking(payload)
        booking_id = create_response.json()["bookingid"]
        resource_registry("booking", booking_id)

        response = booking_helper.get_booking_by_id(booking_id)
        body = response.json()
        AssertHelper.assert_field_equals(body, "firstname", payload["firstname"])
        AssertHelper.assert_field_equals(body, "lastname", payload["lastname"])
        AssertHelper.assert_field_equals(body, "totalprice", payload["totalprice"])
        AssertHelper.assert_field_equals(body, "depositpaid", payload["depositpaid"])
        AssertHelper.assert_field_equals(body, "bookingdates", payload["bookingdates"])

    @allure.story("Response shape matches the documented Booking schema exactly")
    def test_get_booking_by_id_matches_booking_schema(self, booking_helper, resource_registry):
        """Endpoint inventory: GET /booking/{id} (Booking response schema ref)
        case: TC-get-booking-id-contract-schema-booking-shape"""
        payload = booking_payload_unique()
        create_response = booking_helper.create_booking(payload)
        booking_id = create_response.json()["bookingid"]
        resource_registry("booking", booking_id)
        booking_helper.get_booking_by_id(booking_id)

    @allure.story("A booking id that does not exist returns 404")
    def test_get_booking_by_nonexistent_id_returns_404(self, booking_helper, resource_registry, auth_cookie_header):
        """Observed live (context/schema-validation-report.md row 23): `404`, plain-text body
        `Not Found`. The id is made nonexistent deterministically — created, then deleted — rather
        than guessed, since on a shared instance any guessed id could be someone else's booking.
        case: TC-get-booking-id-negative-nonexistent-id"""
        create_response = booking_helper.create_booking(booking_payload_unique())
        booking_id = create_response.json()["bookingid"]
        resource_registry("booking", booking_id)
        booking_helper.delete_booking(booking_id, headers=auth_cookie_header, status_code=201)

        response = booking_helper.get_booking_by_id(booking_id, status_code=404)
        AssertHelper.assert_equals(response.text, "Not Found", context="404 body ")
