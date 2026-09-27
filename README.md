# Restful-Booker API Test Automation

![CI](https://github.com/Anusreepsuresh074/restful-booker-api-automation/actions/workflows/ci.yml/badge.svg)
**[Live test report](https://anusreepsuresh074.github.io/restful-booker-api-automation/)**

A Python + pytest API test automation suite for [Restful-Booker](https://restful-booker.herokuapp.com) — a public practice API simulating a hotel booking system (login, then full CRUD on a booking resource).

**27 tests**, covering all 8 endpoints across happy-path, negative, boundary, auth/authz, and contract/schema cases — each traced back to a documented business rule. Every write is verified with a follow-up read (not just trusted on its own response), and every response is checked against a resolved JSON Schema, not just a status code. Results are reported through [Allure](https://allurereport.org/).

```
27 passed in ~20s (parallel, -n auto)  →  https://restful-booker.herokuapp.com (live)
```

## Why this project

Most "API testing" demos stop at asserting a status code. This one goes further, on purpose:

- **Read-your-write verification** — a `2xx` on `POST`/`PUT`/`PATCH`/`DELETE` only proves the server *accepted* the request, not that it *persisted*. Every write test follows up with a real `GET` (or, for deletes, confirms a `404`) to prove the change actually stuck.
- **Contract/schema validation, not just status codes** — every response is checked against a resolved JSON Schema (required fields, types, no undocumented extra fields), so a silently-renamed field or a type change gets caught even if the status code still looks fine.
- **No fabricated assertions** — a few of this API's behaviors weren't documented anywhere upfront (what does `POST /auth` return on bad credentials? what happens if you `PUT` with a partial body?). Rather than guessing, those test cases were written to assert conservatively, then run live to observe the real answer — see `context/schema-validation-report.md` for exactly what was found.
- **Shared-instance-safe test data** — this is a public, shared demo API that resets every ~10 minutes. Every test creates its own uniquely-named data and only ever asserts on what it created, never on exact totals.

## Architecture

A layered structure, so a change to one thing (a field name, an endpoint path) means editing exactly one file, not twenty:

```
src/
├── constants/endpoints/   # URL paths, as named constants
├── payload/               # request-body factories (test data)
├── schema/                # JSON Schema "rulebooks" for valid responses
├── helper/                # one class per feature — HTTP call + assertions, combined
└── core/
    ├── api_base.py        # the ONE place every HTTP call goes through
    └── assert_helper.py   # the ONE place every assertion goes through
tests/
├── ping/, auth/, booking/ # the actual test files, one method per test case
└── conftest.py            # shared fixtures: auth token, headers, helper instances
```

No test or helper ever calls `requests` directly, and no test ever writes a bare `assert` — both funnel through `ApiBase` and `AssertHelper` respectively, which keeps every request/response logged and Allure-attached (with credentials redacted) and every failure message specific enough to debug without re-running anything.

### This is the Page Object Model, adapted for an API instead of a browser

POM's actual principle isn't UI-specific: tests never talk to the underlying driver/library directly, they call methods on an object that encapsulates that knowledge — so a change to the app under test means editing one file, not every test. This project applies that same principle to an API (sometimes called a **Service Object Model** for exactly this reason):

| POM concept (UI testing) | This project's equivalent |
|---|---|
| A Page Object class per screen | A Helper class per feature — `PingHelper`, `AuthHelper`, `BookingHelper` (`src/helper/`) |
| Page methods (`login_page.click_submit()`) | Helper methods (`booking_helper.create_booking(...)`) |
| Locators centralized in the page object | Endpoint paths centralized as constants (`src/constants/endpoints/`) |
| Tests never call Selenium directly | Tests never call `requests` directly — enforced via `ApiBase` |
| A `BasePage` with shared driver logic | `ApiBase` — the one class every HTTP call goes through |

One deliberate departure from the textbook version: classic POM tutorials often have every Page Object *inherit* from `BasePage`. Here, `BookingHelper` doesn't inherit from `ApiBase` — it *holds* one (`self.api_base = api_base`), i.e. composition over inheritance. Two extra layers exist here with no real UI-testing equivalent: `src/payload/` (request-body factories) and `src/schema/` (JSON Schema response contracts) — API testing needs to build request bodies and validate response shapes in ways a browser test never has to.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime deps (pinned) + ruff, pre-commit
pre-commit install                    # lint + format on every commit

# credentials for /auth — this API's one fixed public demo login
export AUTH_USERNAME=admin
export AUTH_PASSWORD=password123

pytest --env dev -v
```

Generate the Allure report from a run's results:
```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

Run just the fast smoke subset, or the full marked regression suite:
```bash
pytest -m smoke        # 9 tests — the fast, PR-gating subset
pytest -m regression   # all 27 — every test carries this marker
pytest -n auto         # in parallel, one worker per CPU core
ruff check . && ruff format --check .   # lint
```

## CI

`.github/workflows/ci.yml`:

- **Lint** (ruff check + format) gates every run.
- **Smoke suite** on every push and PR — the fast gate, with a JUnit test summary on the run page.
- **Full regression suite** nightly at 02:00 UTC and on demand (Actions → CI → Run workflow).
- **Allure report** with run-over-run history, published to [GitHub Pages](https://anusreepsuresh074.github.io/restful-booker-api-automation/) after every non-PR run.
- **Dependabot** proposes dependency and action updates weekly.

It needs two repository secrets (Settings → Secrets and variables → Actions): `AUTH_USERNAME` and `AUTH_PASSWORD`.

## What's actually in this repo

| Path | What it is |
|---|---|
| `context/api-context.md` | Resolved API surface + business rules (endpoints, auth, quirks like `DELETE` returning `201`) |
| `context/api-auth.md` | How authentication works, token handling, negative-auth states |
| `context/test-case-matrix.md` | The 27-row test case inventory this suite was built from, each row traced to a rule |
| `context/schema-validation-report.md` | Live findings from actually running the suite — including behaviors that were unconfirmed until observed |
| `src/`, `tests/` | The framework and test suite itself |
| `config/config.yaml` | Environment config (this API only really has one: the shared public instance) |

## The tooling behind it

This project's framework and test suite were built through a structured, repeatable AI-assisted workflow (my own Claude Code skills — `skills/` and `agents/` in this repo): discover the API's surface and business rules, resolve auth, design a reviewed test-case matrix, generate the pytest suite, execute it live, and validate real responses against schema — with a human review checkpoint before any test code is generated. `context/*.md` documents each stage's output. The skills themselves are a reusable, project-agnostic suite (see `skills/<name>/SKILL.md` for each one's full spec) — this repo is both the tooling and its first real, executed application.
