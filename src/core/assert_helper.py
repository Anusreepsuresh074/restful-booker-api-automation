import re

import jsonschema


class AssertHelper:
    """Every assertion in generated tests/helpers goes through here — never a bare `assert`."""

    @staticmethod
    def assert_schema(instance, schema: dict):
        try:
            jsonschema.validate(instance=instance, schema=schema)
        except jsonschema.ValidationError as e:
            raise AssertionError(f"Schema validation failed: {e.message}. Instance: {instance!r}") from e

    @staticmethod
    def assert_status_code(response, expected: int):
        assert response.status_code == expected, (
            f"Expected status {expected}, got {response.status_code}. Body: {response.text[:500]}"
        )

    @staticmethod
    def assert_equals(actual, expected, context: str = ""):
        assert actual == expected, f"Expected {context}{expected!r}, got {actual!r}"

    @staticmethod
    def assert_not_equal(actual, unexpected, context: str = ""):
        assert actual != unexpected, f"Expected {context}to differ from {unexpected!r}, both were {actual!r}"

    @staticmethod
    def assert_is_instance(value, expected_type, context: str = ""):
        assert isinstance(value, expected_type), (
            f"Expected {context} to be of type {expected_type.__name__}, got {type(value).__name__} ({value!r})"
        )

    @staticmethod
    def assert_status_code_in(response, expected_codes):
        assert response.status_code in expected_codes, (
            f"Expected status in {expected_codes}, got {response.status_code}. Body: {response.text[:500]}"
        )

    @staticmethod
    def assert_content_type(response, expected_substring: str = "application/json"):
        content_type = response.headers.get("Content-Type", "")
        assert expected_substring in content_type, (
            f"Expected Content-Type containing '{expected_substring}', got '{content_type}'"
        )

    @staticmethod
    def assert_field_equals(body: dict, field: str, expected, path: str = ""):
        actual = body.get(field)
        assert actual == expected, f"Expected {path}{field}={expected!r}, got {actual!r}. Full body: {body}"

    @staticmethod
    def assert_field_present(body: dict, field: str, path: str = ""):
        assert field in body, f"Expected field {path}{field} to be present. Full body: {body}"

    @staticmethod
    def assert_field_absent(body: dict, field: str, path: str = ""):
        assert field not in body, f"Expected field {path}{field} to be absent. Full body: {body}"

    @staticmethod
    def assert_field_type(body: dict, field: str, expected_type, path: str = ""):
        value = body.get(field)
        assert isinstance(value, expected_type), (
            f"Expected {path}{field} to be of type {expected_type.__name__}, got {type(value).__name__} ({value!r})"
        )

    @staticmethod
    def assert_contains(haystack, needle, context: str = ""):
        assert needle in haystack, f"Expected {context}to contain {needle!r}, got {haystack!r}"

    @staticmethod
    def assert_not_contains(haystack, needle, context: str = ""):
        assert needle not in haystack, f"Expected {context}not to contain {needle!r}, got {haystack!r}"

    @staticmethod
    def assert_matches_regex(value: str, pattern: str, context: str = ""):
        assert isinstance(value, str) and re.fullmatch(pattern, value), (
            f"Expected {context}to match {pattern!r}, got {value!r}"
        )

    @staticmethod
    def assert_field_not_empty(body: dict, field: str, path: str = ""):
        value = body.get(field)
        assert value, f"Expected {path}{field} to be present and non-empty, got {value!r}"

    @staticmethod
    def assert_implies(antecedent: bool, consequent: bool, antecedent_desc: str, consequent_desc: str):
        """Asserts `antecedent -> consequent`. Used for response-field invariants that must hold
        for a resource in any state, rather than pinning an assertion to one record's values."""
        assert (not antecedent) or consequent, f"Invariant violated: when {antecedent_desc}, expected {consequent_desc}"

    @staticmethod
    def assert_iff(left: bool, right: bool, left_desc: str, right_desc: str):
        """Asserts `left <-> right` — both sides must agree. Same purpose as assert_implies, for
        rules where the response fields are expected to be mutually consistent in both directions."""
        assert left == right, (
            f"Invariant violated: {left_desc} is {left}, but {right_desc} is {right} — these must agree"
        )
