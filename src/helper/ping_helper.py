import allure

from src.constants.endpoints.ping_ep import PING


class PingHelper:
    def __init__(self, api_base):
        self.api_base = api_base

    @allure.step("Call GET /ping health check")
    def ping(self):
        return self.api_base.get(PING)
