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

    @allure.step("Full-replace update a booking (PUT)")
    def update_booking(self, booking_id, payload: dict, headers: dict = None, status_code: int = 200):
        response = self.api_base.put(BOOKING_BY_ID.format(id=booking_id), json=payload, headers=headers)
        AssertHelper.assert_status_code(response, status_code)
        if status_code == 200:
            AssertHelper.assert_schema(response.json(), BOOKING_SCHEMA)
        return response

    @allure.step("Attempt a full-replace update without asserting a specific outcome")
    def attempt_update_booking_raw(self, booking_id, payload: dict, headers: dict = None):
        return self.api_base.put(BOOKING_BY_ID.format(id=booking_id), json=payload, headers=headers)

    @allure.step("Partially update a booking (PATCH)")
    def partial_update_booking(self, booking_id, payload: dict, headers: dict = None, status_code: int = 200):
        response = self.api_base.patch(BOOKING_BY_ID.format(id=booking_id), json=payload, headers=headers)
        AssertHelper.assert_status_code(response, status_code)
        if status_code == 200:
            AssertHelper.assert_schema(response.json(), BOOKING_SCHEMA)
        return response

    @allure.step("Delete a booking")
    def delete_booking(self, booking_id, headers: dict = None, status_code: int = 201):
        response = self.api_base.delete(BOOKING_BY_ID.format(id=booking_id), headers=headers)
        AssertHelper.assert_status_code(response, status_code)
        return response
