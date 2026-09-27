---
name: create-framework-structure
description: Designs and builds a brand-new API automation framework from scratch, one architectural layer at a time — confirms the stack, presents the full target folder structure with the reasoning behind it, then creates each layer (config, HTTP core, assertions, constants, payloads, schema, helpers, utils, logging, reporting, CI, docs) only after explaining what it is, why it exists, and how it connects to the rest. Never generates test cases, test scripts, or business-specific API code — those belong to api-test-design, pytest-api, and get-api-auth. Use once, at the start of a new API automation project, when there is no existing framework to extend.
---

# Create Framework Structure

Builds a production-ready API automation framework from a blank repo. This
skill's whole job is architecture and scaffolding — the empty skeleton that
`get-api-auth`, `api-test-design`, and `pytest-api` (both its generation and
validation phases) all build on top of later. It never writes a test case, a test script, or any
API-specific business logic itself.

The point is deliberate, explained construction, not a single bulk file
dump: plan the whole architecture and get it confirmed, then create one
layer at a time, stating what's being created, why it's needed, where it
belongs, and how it connects to what already exists — *before* creating it,
not as an afterthought in a summary.

## When to use

- Once, at the very start of a new API automation project — before
  `get-context`, `get-api-auth`, or any other skill in this suite has
  anything to read.
- Never mid-project "to add a folder" — if a framework already exists,
  extend it by hand or via `pytest-api`'s reuse-before-creating step; this
  skill is for greenfield only.

## Guardrails

These are hard constraints, not style preferences. If a step below seems to
conflict with one of these, the guardrail wins.

- **Plan before you build.** Present the full target folder tree (see
  "Target architecture" below) with a one-line purpose per folder, and get
  the user's confirmation on the stack and layout before creating anything.
  Don't silently start writing files from the first message.
- **One layer at a time, explained as you go.** After the plan is confirmed,
  create layers in the order listed under "Build phases," and for each one
  state what/why/where/how *before* writing the files — never batch-generate
  the whole tree in one shot even after confirmation.
- **Create only what the current phase needs.** Don't pre-create empty
  per-feature folders, placeholder test files, or speculative helpers for
  APIs that don't exist yet in this project. `src/constants/endpoints/`,
  `src/payload/`, `src/schema/`, and `src/helper/` start as empty,
  documented directories — `pytest-api` populates them per feature later.
- **Stay compatible with what downstream skills expect.** `pytest-api`'s own
  "Project layout (default)" section hardcodes the shape this skill must
  produce (`src/core/api_base.py`, `src/core/assert_helper.py`,
  `src/constants/endpoints/`, `src/payload/`, `src/schema/`, `src/helper/`,
  `tests/<feature>/`, root + `tests/` `conftest.py`). Don't invent a
  different top-level layout — if a project genuinely needs a different
  shape, that's a "Project overrides" entry in the project's agent config,
  not a fork of this skill's defaults.
- **Auth is a hook here, not an implementation.** This skill creates the
  *place* auth fixtures will live (`tests/conftest.py`) and wires no real
  login logic into it — resolving and documenting the actual auth mechanism
  is `get-api-auth`'s job entirely. Don't duplicate that work here.
- **No business-specific content.** Don't invent example endpoints,
  payloads, or schemas for an API this project hasn't named. Placeholder
  directories stay empty (with a short README or `.gitkeep`, not fabricated
  sample code) until a real feature exists.
- **Centralize configuration.** Base URLs, timeouts, and environment
  selection live in one place (`config/` + a single loader module) — never
  scattered as literals across multiple files.
- **Separate concerns strictly.** HTTP mechanics (`src/core/api_base.py`),
  assertions (`src/core/assert_helper.py`), constants, payloads, schemas,
  and helpers are distinct layers with a single responsibility each — don't
  collapse them to save a file.
- **Meaningful names only.** No `utils2.py`, `helper_final.py`, `misc/`.
  Every folder and file name should say what it holds.
- **Every Python package directory gets an `__init__.py`.** `src/` and every
  subdirectory under it (`config/`, `core/`, `constants/`, `constants/endpoints/`,
  `payload/`, `schema/`, `helper/`, `utils/`), plus `tests/`, are Python
  packages, not just folders — each one gets its own `__init__.py` (even
  empty) created in the same phase that creates the directory, never added
  as a cleanup pass afterward.

## Step 0 — Confirm scope

Before designing anything, confirm (ask if not already stated in
conversation or in an existing `.claude/agents/api-automation-agent.md`):

1. **Programming language and test framework.** This suite's other skills
   (`pytest-api` in particular) are written against Python + pytest +
   Allure reporting — that's the default and the path with zero downstream
   friction. If the user wants something else, say plainly that `pytest-api`
   (generation and validation both) assumes Python/pytest and would need a
   documented override, rather than silently building a mismatched scaffold.
2. **Reporting tool.** Default Allure (matches `pytest-api`'s
   `@allure.step`/`@allure.feature`/`@allure.story` decorators). Confirm if
   the project wants something else (e.g. `pytest-html`, JUnit XML only).
3. **CI/CD platform.** Default to the one matching the repo's remote
   (GitHub → `.github/workflows/`, Bitbucket → `bitbucket-pipelines.yml`,
   GitLab → `.gitlab-ci.yml`) — confirm if CI lives elsewhere (e.g. Jenkins).
4. **Environments.** Which environments need config entries (dev/staging/
   prod, or project-specific names) and what varies between them (base URL
   at minimum).

Don't proceed past this step on assumptions where the answer materially
changes the folder structure.

## Target architecture

Present this full tree to the user, with the purpose column, before
creating anything:

```
.
├── config/
│   └── config.yaml              # per-environment base URLs, timeouts
├── src/
│   ├── __init__.py              # every src/ subdirectory below is a package — each gets one
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_loader.py     # single place that reads config.yaml + env overrides
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api_base.py          # all HTTP calls go through here — never raw requests in tests
│   │   └── assert_helper.py     # all assertions go through here — never bare `assert`
│   ├── constants/
│   │   ├── __init__.py
│   │   └── endpoints/           # <feature>_ep.py path constants — empty until pytest-api adds features
│   │       └── __init__.py
│   ├── payload/                 # <feature>_payload.py request-body factories — empty until populated
│   │   └── __init__.py
│   ├── schema/                  # <feature>_schema.py response schemas — empty until populated
│   │   └── __init__.py
│   ├── helper/                  # <feature>_helper.py orchestration (calls api_base + assert_helper)
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # shared logging setup
├── tests/
│   ├── __init__.py
│   └── conftest.py              # shared fixtures: auth tokens (from get-api-auth), cleanup collectors
├── conftest.py                  # root: pytest_addoption (--env etc.), env bootstrap
├── context/                     # created by get-context / get-api-auth / api-test-design, not this skill
├── reports/                     # generated Allure/HTML output — gitignored
├── requirements.txt             # or pyproject.toml, per Step 0 confirmation
├── pytest.ini
├── .env.example
├── bitbucket-pipelines.yml      # or the confirmed CI platform's equivalent
└── README.md
```

Note in the presentation: `src/constants/endpoints/`, `src/payload/`,
`src/schema/`, and `src/helper/` are intentionally empty at this stage —
they're the shelves `pytest-api` stocks per feature once real endpoints
exist. `context/` isn't this skill's to create; `get-context` makes it when
it first writes `context/api-context.md`.

## Build phases

Create these in order. For each phase, state what/why/where/how in
conversation *before* writing the files, then create just that phase's
files before moving on — don't jump ahead.

1. **Configuration management** — `src/__init__.py`, `config/config.yaml`,
   `src/config/__init__.py`, `src/config/config_loader.py`, `.env.example`.
   *Why:* every other layer needs a base URL/timeout/environment without
   hardcoding it. *How it connects:* `api_base.py` and test fixtures both
   read through this loader, never the YAML file directly.

2. **HTTP core** — `src/core/__init__.py`, `src/core/api_base.py`.
   *Why:* a single chokepoint for every HTTP call means logging, timeouts,
   and base-URL handling live in one place. *How it connects:* every
   `<feature>_helper.py` `pytest-api` generates later calls this instead of
   `requests`/`httpx` directly.

3. **Assertions core** — `src/core/assert_helper.py` (package already
   initialized in phase 2).
   *Why:* consistent, readable failure messages and no bare `assert`
   scattered through generated tests. *How it connects:* `pytest-api`'s
   generated helpers and tests call this for every check, including schema
   assertions its own validation phase later benchmarks against.

4. **Constants, payloads, schema, helper directories** —
   `src/constants/__init__.py`, `src/constants/endpoints/__init__.py`,
   `src/payload/__init__.py`, `src/schema/__init__.py`,
   `src/helper/__init__.py`, each directory also getting a short
   `README.md` (or `.gitkeep`) stating what belongs there and that
   `pytest-api` populates it per feature.
   *Why:* establishes the shape without fabricating content for an API
   that isn't defined yet. *How it connects:* these are exactly the paths
   `pytest-api`'s "Project layout" step writes into.

5. **Utilities & logging** — `src/utils/__init__.py`, `src/utils/logger.py`.
   *Why:* consistent log formatting across the framework. *How it
   connects:* `api_base.py` and generated helpers both log through this.

6. **Fixture roots** — root `conftest.py` (pytest_addoption for `--env`
   etc., env bootstrap), `tests/__init__.py`, and `tests/conftest.py`
   (empty shared-fixture file with a comment noting that auth fixtures land
   here once `get-api-auth` has documented the mechanism — this skill does
   not invent a token fixture itself).
   *Why:* gives `pytest-api` a known place to add fixtures instead of
   guessing. *How it connects:* directly consumed by every generated test.

7. **Reporting** — Allure (or the confirmed tool) wiring in `pytest.ini`
   (e.g. `--alluredir=reports/allure-results`), `reports/` added to
   `.gitignore`.
   *Why:* test runs need a report output without manual setup per run.

8. **CI/CD readiness** — a minimal `bitbucket-pipelines.yml` (or the
   confirmed platform's config) that installs deps and runs `pytest`.
   *Why:* the framework should be runnable in CI from day one, even before
   real tests exist. Keep it minimal — don't invent stages/environments the
   user hasn't asked for.

9. **Documentation** — `README.md` describing the folder structure (link
   back to the same purpose table used above) and how to run the suite
   locally.
   *Why:* anyone opening the repo cold — including a future run of
   `get-context` — can see the framework's shape without re-deriving it.

## Limitations

This skill is only responsible for creating the framework structure. It
must **not**:

- Generate API test cases (that's `api-test-design`).
- Generate API automation scripts (that's `pytest-api`).
- Execute tests.
- Analyze test failures.
- Implement business-specific API logic, endpoints, payloads, or schemas.
- Resolve or document the real authentication mechanism (that's
  `get-api-auth`) — this skill only creates the empty fixture file it will
  land in.

If asked to do any of the above mid-conversation, say which skill owns that
responsibility instead of doing it here.

## Notes for reuse across projects

- Never hardcode a project-specific base URL, API name, or business domain
  in this skill file itself — Step 0's confirmation and the target tree
  above are what stay generic across every project this suite is used on.
- If a project's stack genuinely differs from Python/pytest/Allure, build
  the equivalent layers under equivalent names, but flag in your summary
  that `pytest-api` (generation and validation both) assumes the Python
  defaults and the project's agent config needs a "Project overrides" entry
  recording the difference.
- Re-running this skill on a project that already has a framework is out of
  scope — point the user at extending the existing structure by hand
  instead of regenerating it.
