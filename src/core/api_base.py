import allure
import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)

_SENSITIVE_KEYS = {"password", "token"}


def _redact(value):
    """Masks known credential fields before anything gets logged or attached to the Allure
    report — request bodies (e.g. POST /auth) carry a plaintext password that has no business
    appearing in a report, even for a non-secret demo credential."""
    if isinstance(value, dict):
        return {
            key: ("***" if key.lower() in _SENSITIVE_KEYS else _redact(val))
            for key, val in value.items()
        }
    return value


class ApiBase:
    """Every HTTP call in this framework goes through here — never raw requests/httpx in tests or helpers."""

    def __init__(self, config):
        self.base_url = config.base_url
        self.timeout = config.timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    @allure.step("{method} {path}")
    def _request(self, method: str, path: str, headers=None, params=None, json=None, **kwargs):
        url = self._url(path)
        redacted_json = _redact(json)
        logger.info("%s %s | params=%s | json=%s", method, url, params, redacted_json)
        self._attach("Request", f"{method} {url}\nparams={params}\njson={redacted_json}")
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=self.timeout,
            **kwargs,
        )
        logger.info("-> %s %s", response.status_code, response.text[:500])
        self._attach("Response", f"status_code={response.status_code}\n{response.text[:500]}")
        return response

    @staticmethod
    def _attach(name: str, body: str) -> None:
        allure.attach(body, name=name, attachment_type=allure.attachment_type.TEXT)

    def get(self, path: str, headers=None, params=None, **kwargs):
        return self._request("GET", path, headers=headers, params=params, **kwargs)

    def post(self, path: str, headers=None, json=None, params=None, **kwargs):
        return self._request("POST", path, headers=headers, json=json, params=params, **kwargs)

    def put(self, path: str, headers=None, json=None, params=None, **kwargs):
        return self._request("PUT", path, headers=headers, json=json, params=params, **kwargs)

    def patch(self, path: str, headers=None, json=None, params=None, **kwargs):
        return self._request("PATCH", path, headers=headers, json=json, params=params, **kwargs)

    def delete(self, path: str, headers=None, params=None, **kwargs):
        return self._request("DELETE", path, headers=headers, params=params, **kwargs)
