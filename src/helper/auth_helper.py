import allure

from src.constants.endpoints.auth_ep import AUTH
from src.core.assert_helper import AssertHelper
from src.payload.auth_payload import auth_payload
from src.schema.auth_schema import AUTH_TOKEN_SCHEMA


class AuthHelper:
    def __init__(self, api_base):
        self.api_base = api_base

    # Steps here are context managers, not `@allure.step`, so the credentials passed in are
    # never recorded as Allure step parameters (ApiBase attaches the redacted request instead).
    def authenticate(self, username: str = None, password: str = None, status_code: int = 200):
        with allure.step("Authenticate and get a token"):
            response = self.api_base.post(AUTH, json=auth_payload(username, password))
            AssertHelper.assert_status_code(response, status_code)
            if status_code == 200:
                AssertHelper.assert_schema(response.json(), AUTH_TOKEN_SCHEMA)
            return response

    def authenticate_raw(self, payload: dict):
        with allure.step("Attempt authentication with an arbitrary payload, no status assumed"):
            return self.api_base.post(AUTH, json=payload)

    @staticmethod
    def cookie_header(token: str) -> dict:
        return {"Cookie": f"token={token}"}
