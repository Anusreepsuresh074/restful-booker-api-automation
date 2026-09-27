# Generated-code conventions (greenfield default)

`pytest-api`'s **Match existing conventions** guardrail says: read the repo first, and make generated code look like it belongs there. This file is what to follow when there's nothing to match yet — a greenfield project where `create-framework-structure` has scaffolded the layers but no feature code exists.

**Precedence:** an existing convention in the project always wins over this file. If the repo already names its endpoint constants one way, or already has an assertion helper with different method names, follow the repo. Use this file only to fill genuine blanks, and never rewrite existing files to match it.

These are conventions for code this skill *generates*. They are not new guardrails — the hard constraints stay in `SKILL.md`.

## Layering — what may import what

```
tests/<feature>/test_*.py   →  helpers, fixtures, _td.py            (never ApiBase, never requests)
src/helper/<feature>_helper.py →  ApiBase, AssertHelper, payload, schema, endpoints
src/payload/<feature>_payload.py →  nothing (pure functions)
src/schema/<feature>_schema.py   →  nothing (plain dicts)
src/constants/endpoints/<feature>_ep.py → nothing (plain strings)
src/core/api_base.py        →  the HTTP library, config, logger
```

Rules that follow from that:

- **No raw `requests`/`httpx` anywhere except `src/core/api_base.py`.** A test or helper that imports the HTTP library directly is a layering break, not a shortcut.
- **No bare `assert` in tests or helpers.** Every check goes through `AssertHelper`. If the check you need doesn't exist there yet, add one method to `AssertHelper` (with a message naming the field and both values) rather than inlining an `assert`.
- **No HTTP call in a test method.** Tests call helper methods; helpers call `ApiBase`. A test body should read as a sequence of business steps.
- **Payload factories are pure.** They take arguments and return a dict. No I/O, no randomness that isn't collision-safety, no reading fixtures, no calling the API.
- **Schemas are data.** `src/schema/<feature>_schema.py` holds plain JSON-Schema dicts as module-level constants — no logic, no conditionals.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Endpoint constant | `UPPER_SNAKE`, one per operation, path template with `{}` placeholders | `UPDATE_GROUP_STATUS = "/v1/organisation/{org_id}/branch/{branch_id}/group/{group_id}/{status}"` |
| Payload factory | `<action>_<resource>_payload` | `create_group_payload(...)` |
| Schema constant | `<OPERATION>_<KIND>_SCHEMA` | `CREATE_GROUP_RESPONSE_SCHEMA`, `ERROR_STATUS_SCHEMA` |
| Helper class | `<Feature>Helper`, one per feature | `GroupHelper` |
| Helper method | verb-first, matching the business action, not the HTTP verb | `update_group_status(...)`, not `patch_group(...)` |
| Test file | `test_NNN_<feature>_<case-type-or-theme>.py`, numbered per feature folder | `test_004_group_status_auth_authz.py` |
| Test class | `Test<Feature><Theme>` | `TestGroupStatusHappy` |
| Test method | exactly the matrix **Test name** column | `test_activate_inactive_group_happy` |
| Test-data class | `<Feature>TestData` in `<feature>_td.py` | `GroupStatusTestData` |

Path-template placeholders use the same names as the fixtures/arguments that fill them, so `.format(...)` calls read without a lookup.

## Test method shape

One matrix row → one test method. Keep the body in three visible parts, no section comments needed:

1. **Arrange** — fixtures, test data, any setup calls made through a helper (a setup call is still a helper call, never a raw request).
2. **Act** — the single call the row is actually about.
3. **Assert** — the Expected column, through `AssertHelper`, plus the read-back call for a 2xx write (see below).

Each method carries:

- A docstring starting with the matrix **Rule** (`RULE-3: activating a CustomTerm-interval schedule is rejected`) followed by `Verifies: <the matrix's plain-English intent>`. This is the traceability the Rule column is for.
- `@allure.title("Sl No. <n> — <short case>")` so a report row maps back to a matrix row.
- Class-level `@allure.feature`, `@allure.story`, and `@pytest.mark.<feature>` (plus the scope markers `ci-integration` registers, e.g. `smoke`/`regression`, once those exist).

Don't wrap a test body in `try/except`. A raised `AssertionError` is the result; swallowing it hides the finding.

## Status codes and negative cases

Helpers take `status_code: int = <success>` and assert it. A negative row passes the expected failure code instead of duplicating the helper:

```python
group_helper.update_group_status(headers, ..., status="disabled", status_code=400)
```

The helper validates against the success schema when the status is the success one and against the documented error schema otherwise. That keeps `contract-schema` and `error-shape` rows from needing a second code path.

## Read-your-write (Step 6.5)

For any row expecting a 2xx on `POST`/`PUT`/`PATCH`/`DELETE`, the write is not the assertion — the read-back is:

```python
group_helper.update_group_status(headers, ..., status="inactive")
group_helper.assert_group_status_is(headers, ..., group_id, expected="inactive")   # documented GET
```

- The read-back lives in the helper as its own `@allure.step` method, called inline from the same test method — never a separate test.
- It reuses the auth fixture the write used.
- Only wire it when `context/api-context.md` documents a GET for that resource. If it doesn't, classify `no-read-endpoint-available` and assert the write response alone — never invent the GET.
- A setup call that creates a resource (`create_group`) is itself a 2xx write and gets the same treatment as the row's primary call.

## Created-resource registry

Every test that causes a resource to exist registers it — including resources created in *setup*, not just the one the row is about:

```python
def test_deactivate_active_group_happy(self, group_helper, auth_token, ..., created_group_ids):
    group = group_helper.create_group(auth_headers(auth_token), org_id, branch_id)
    created_group_ids(group["id"])
```

One shared registry for the project (`reports/created-resources.jsonl` by default), one entry per resource with type, id, environment, and creation timestamp. The fixture only appends — no post-yield delete, no finalizer, no `atexit`. Clearing is `teardown`'s job, on an explicit yes.

## Fixtures

- Session scope for anything expensive and read-only across tests (config, `ApiBase`, helpers, the login and the ids it yields). Function scope for per-test state (invalid-token mutations, registries, factories).
- A fixture that returns a callable (a registrar, a payload factory) returns the inner function — it doesn't perform the action at fixture time.
- Auth fixtures read credentials from the environment and never hold a literal. Prefer an explicit lookup that fails loudly with the variable's name over a silent `None` that surfaces later as a confusing 401.
- Don't duplicate a fixture in `tests/<feature>/conftest.py` that already exists in `tests/conftest.py`.

## Parametrization

Use `_td.py` when a row has multiple input variants; keep single-value cases inline. Every `pytest.param` gets an explicit `id=` so the Allure/JUnit test name stays readable and stable across runs (test identity is what `flaky-test-triage` matches on — an unstable id looks like a brand-new test with no history).

```python
class GroupStatusTestData:
    INVALID_STATUSES = [
        pytest.param("Active", id="wrong-case"),
        pytest.param("disabled", id="invalid-enum"),
    ]
```

Name constants for what they mean to the *rule*, not for their literal value, and comment the matrix row each one serves.

## Imports and formatting

- Standard library, then third-party, then first-party (`src.*`, `tests.*`), separated by blank lines.
- Absolute imports from the project root (`from src.helper.group_helper import GroupHelper`) — no relative imports across layers.
- 4-space indent, one class per test file unless rows genuinely share a story, module docstring only where the file's scope isn't obvious from its name.
- No commented-out code and no `TODO` in generated output. An unfinished row is a skipped row reported in the summary and the traceability record, not a comment left in a file.

## Package init

Every `tests/<feature>/` directory gets an `__init__.py` created in the same action that creates the directory. Same for any new `src/` subpackage. Not a cleanup pass.
