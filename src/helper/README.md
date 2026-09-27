# Helper

`<feature>_helper.py` — orchestration layer per feature (calls `api_base.py` + `assert_helper.py`).
One `@allure.step`-decorated method per distinct API call — makes the HTTP request, asserts the
status code, and runs schema validation on a successful response, so test files never touch
`ApiBase` or raw assertions directly.
