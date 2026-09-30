import allure

from src.constants.endpoints.booking_ep import BOOKING, BOOKING_BY_ID
from src.core.assert_helper import AssertHelper
from src.schema.booking_schema import (
    BOOKING_ID_LIST_SCHEMA,
    BOOKING_SCHEMA,
    CREATE_BOOKING_RESPONSE_SCHEMA,
)


class BookingHelper:
    def __init__(self, api_base):
        self.api_base = api_base

    @allure.step("List bookings with optional filters")
    def list_bookings(self, params: dict = None, status_code: int = 200):
        response = self.api_base.get(BOOKING, params=params)
        AssertHelper.assert_status_code(response, status_code)
        if status_code == 200:
            AssertHelper.assert_schema(response.json(), BOOKING_ID_LIST_SCHEMA)
        return response

    @allure.step("Create a booking")
    def create_booking(self, payload: dict, status_code: int = 200):
        response = self.api_base.post(BOOKING, json=payload)
        AssertHelper.assert_status_code(response, status_code)
        if status_code == 200:
            AssertHelper.assert_schema(response.json(), CREATE_BOOKING_RESPONSE_SCHEMA)
        return response

    @allure.step("Get a booking by id")
    def get_booking_by_id(self, booking_id, status_code: int = 200):
        response = self.api_base.get(BOOKING_BY_ID.format(id=booking_id))
        AssertHelper.assert_status_code(response, status_code)
        if status_code == 200:
            AssertHelper.assert_schema(response.json(), BOOKING_SCHEMA)
        return response

    # The write methods below take auth headers (Cookie token / Basic auth), so their steps are
    # context managers rather than `@allure.step` — the decorator would record `headers` as a
    # step parameter and publish the credential in the report.
    def update_booking(self, booking_id, payload: dict, headers: dict = None, status_code: int = 200):
        with allure.step(f"Full-replace update booking {booking_id} (PUT)"):
            response = self.api_base.put(BOOKING_BY_ID.format(id=booking_id), json=payload, headers=headers)
            AssertHelper.assert_status_code(response, status_code)
            if status_code == 200:
                AssertHelper.assert_schema(response.json(), BOOKING_SCHEMA)
            return response

    def attempt_update_booking_raw(self, booking_id, payload: dict, headers: dict = None):
        with allure.step(f"Attempt a full-replace update of booking {booking_id} without asserting an outcome"):
            return self.api_base.put(BOOKING_BY_ID.format(id=booking_id), json=payload, headers=headers)

    def partial_update_booking(self, booking_id, payload: dict, headers: dict = None, status_code: int = 200):
        with allure.step(f"Partially update booking {booking_id} (PATCH)"):
            response = self.api_base.patch(BOOKING_BY_ID.format(id=booking_id), json=payload, headers=headers)
            AssertHelper.assert_status_code(response, status_code)
            if status_code == 200:
                AssertHelper.assert_schema(response.json(), BOOKING_SCHEMA)
            return response

    def delete_booking(self, booking_id, headers: dict = None, status_code: int = 201):
        with allure.step(f"Delete booking {booking_id}"):
            response = self.api_base.delete(BOOKING_BY_ID.format(id=booking_id), headers=headers)
            AssertHelper.assert_status_code(response, status_code)
            return response

    def cleanup_booking(self, booking_id, headers: dict):
        """Teardown delete for a booking a test created. Tolerates one the test already deleted
        (or the shared instance's ~10-minute reset removed): this API answers `405` for a DELETE
        on a nonexistent id, and `404` is accepted too in case that ever changes."""
        with allure.step(f"Clean up booking {booking_id}"):
            response = self.api_base.delete(BOOKING_BY_ID.format(id=booking_id), headers=headers)
            AssertHelper.assert_status_code_in(response, [201, 404, 405])
            return response
