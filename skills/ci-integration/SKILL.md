---
name: ci-integration
description: Upgrades create-framework-structure's minimal CI pipeline stub (bitbucket-pipelines.yml, or the confirmed platform's equivalent) into a CI-grade pipeline — sharded/parallel test execution, an environment matrix (e.g. a PR-triggered smoke run against dev/staging vs. a scheduled nightly-regression run across the full environment set), a confirmed retry policy for transient failures, JUnit-XML/Allure report generation with CI-artifact publishing, failure notifications wired to real results (test failures, pytest-api's schema-validation-phase breaking findings), and — if confirmed — a reports/history/ archiving phase using the platform's own persistent-cache mechanism so flaky-test-triage's cross-run detection has data to work with. Never invents a shard count, environment, marker name, retry count, notification channel, history-retention count, or credential the user hasn't confirmed or that isn't already on disk. Use once create-framework-structure's minimal pipeline exists and pytest-api has generated a real, runnable suite — re-run whenever a new environment, marker, notification channel, or history-retention policy is added.
---

# CI Integration

`create-framework-structure` deliberately stops at a minimal pipeline — installs deps, runs `pytest`, nothing else ("keep it minimal — don't invent stages/environments the user hasn't asked for"). This skill is the deliberate, *confirmed* follow-up that builds the rest out: splitting the suite across parallel workers, running different scope depending on what triggered the run (a fast smoke pass on a PR vs. the full regression suite overnight), and alerting someone when a run fails — the things that make a pipeline actually usable day-to-day instead of just "green because it ran once." Like `create-framework-structure`, it writes real config, not documentation — but every stage, environment, and channel it adds still has to be confirmed first, never invented.

## When to use

- Once `create-framework-structure` has created the minimal pipeline stub **and** `pytest-api` has generated a real, runnable suite — sharding and environment scoping need actual tests/markers to target, not an empty skeleton.
- When the project needs genuine CI-grade behavior: parallel execution, PR-smoke vs. nightly-regression scoping, a retry policy for transient failures, real report artifacts, or automated failure alerts — not just "the pipeline installs deps and runs pytest."
- Whenever a new environment, marker, or notification channel is added and the pipeline needs to catch up.

## Prerequisites (hard stop if missing)

| Input | Typically produced by | Required? |
|---|---|---|
| A CI pipeline file (`bitbucket-pipelines.yml` or the confirmed platform's equivalent) | `create-framework-structure` | **Yes** — if missing, say `Run create-framework-structure first.` and stop |
| A runnable test suite (`tests/`, markers, `pytest.ini`) | `pytest-api` | **Yes** — if missing, say `Run pytest-api first — sharding and environment scoping need real tests to target.` and stop |
| `config/config.yaml` environment entries | `create-framework-structure` | **Yes** — the environment matrix reads real environment names from here, never invented ones |
| `context/schema-validation-report.md` / `create-report` output | `pytest-api`'s validation phase / `create-report` | Optional — enriches failure notifications with breaking-schema-drift context if present |

## Guardrails

These are hard constraints, not style preferences. If a step below seems to conflict with one of these, the guardrail wins.

- **Confirm before you build, same as `create-framework-structure`.** Present the planned additions (which stages, which trigger maps to which environments/marker scope, which notification channel) and get the user's confirmation before editing the pipeline file. Don't silently start rewriting CI config from the first message.
- **Never invent a shard count, environment, marker name, retry count, notification channel, history-retention count, or credential.** Read real environment names from `config/config.yaml`, real marker names from `pytest.ini`/`pyproject.toml` (or propose `smoke`/`regression` and get them confirmed if none exist yet), and ask for the notification tool/channel, shard strategy, rerun count/delay, and history-retention count/mechanism rather than guessing a plausible default silently. For history retention, use the CI platform's own persistent-cache primitive by its real name (e.g. Bitbucket Pipelines' `caches:` block with a fixed, non-lockfile-derived key) — never fabricate a caching mechanism the platform doesn't actually support.
- **Retries are for transient failures, not flaky tests.** This skill's rerun policy (e.g. `pytest-rerunfailures`) exists to absorb infra-level noise — a dropped connection, a slow-starting dev environment — within a single CI run. It is not a diagnostic tool: it doesn't decide a test is flaky, doesn't tag or quarantine anything, and doesn't replace `flaky-test-triage`, which analyzes outcome patterns across runs *after* the fact. If a test needs more than the confirmed rerun count to pass, that's a real failure to report, not something to retry harder.
- **No credentials or secrets in the pipeline file, ever.** Reference the CI platform's own secret/variable store by name only (e.g. `$SLACK_WEBHOOK_URL` as a Bitbucket repository/deployment variable) — never a literal webhook URL, API key, or token value, even a sample one from a doc or from conversation.
- **Marker convention is closed and total once established.** Whatever scope-marker names get confirmed (e.g. `smoke`, `regression`), every generated test must end up tagged into at least one of them. A test with no marker is an Open Question to flag, never something silently left out of every pipeline run without saying so.
- **Sharding must not break test isolation.** Don't split tests in a way that could put two shards through the same shared-state fixture at once (e.g. two shards both creating/deleting the same seed resource). Default to sharding by file/feature, which is safe against `pytest-api`'s per-test collector-fixture cleanup pattern; only shard by raw count/duration if the user explicitly confirms cross-feature isolation is safe for this project.
- **No fabrication.** Every stage, environment mapping, marker reference, and notification trigger in the pipeline must trace back to something real: an environment name actually in `config/config.yaml`, a marker actually registered and applied to real tests, a report path `pytest-api`/`create-report` actually produce. Never wire in a plausible-looking stage for something that doesn't exist yet.
- **Read-only outside what this skill owns.** Don't modify `context/*.md`, generated test files under `tests/`/`src/`, or anything `get-context`/`api-test-design`/`pytest-api`/`create-report` produced. This skill's writes are scoped to: the CI pipeline file(s), `pytest.ini`/`pyproject.toml` (marker registration and parallelization config only), and `config/config.yaml` (only to confirm/reference existing environment entries — never to invent a new environment's base URL without the user supplying it).
- **Don't re-derive or re-run what other skills own.** Pull environment names from `config/config.yaml`, test paths/markers from the suite `pytest-api` generated, and failure content from `context/schema-validation-report.md`/`create-report`'s output — don't regenerate tests, re-validate schemas, or produce the human-facing report itself here.
- **This skill edits CI config; it does not trigger a run.** It doesn't execute the pipeline, doesn't call the live API, and doesn't invoke `pytest` itself to "test" its own changes beyond local syntax/lint checks on the config file, if available.
- **Announce, don't re-ask, for incremental additions.** Once the overall plan is confirmed and built, adding one more already-discussed environment or a config tweak on a later run doesn't need the whole pipeline re-confirmed from scratch — just say what changed.

## Step 0 — Confirm scope

Before editing anything, confirm (ask if not already stated in conversation or recorded in `.claude/agents/api-automation-agent.md`):

1. **CI platform.** Detect from the existing pipeline file on disk (`bitbucket-pipelines.yml` → Bitbucket Pipelines, `.github/workflows/*.yml` → GitHub Actions, `.gitlab-ci.yml` → GitLab CI, `Jenkinsfile` → Jenkins). Confirm if none is unambiguous.
2. **Environments and their trigger mapping.** Read the environment names already in `config/config.yaml`. Ask which subset a PR-triggered run should hit (typically one, e.g. `dev` or `staging`) and which the scheduled nightly-regression run should cover (typically all).
3. **Marker/tagging convention.** Check `pytest.ini`/`pyproject.toml` for existing marker registration. If none exists, propose `smoke` (fast, PR-gating subset) and `regression` (full suite, nightly) and get them confirmed — or use the project's own names if it already has a convention.
4. **Parallelization strategy.** Default to `pytest-xdist` for a Python/pytest project (`-n auto`, or an explicit worker count) sharded by file/feature. Confirm worker count and whether count-based sharding is acceptable instead (see isolation guardrail above).
5. **Retry policy for transient failures.** Confirm whether the pipeline should rerun a failed test automatically (default tool for pytest: `pytest-rerunfailures`) and, if so, the rerun count and delay between attempts (e.g. `--reruns 2 --reruns-delay 5`). If the user doesn't want retries, record that explicitly rather than silently adding a default.
6. **Report formats to generate.** Confirm which report artifacts the pipeline itself should produce beyond what `pytest.ini` already wires (Allure results by default, per `create-framework-structure`) — typically JUnit XML (`--junitxml=reports/junit.xml`) for CI-native test reporting/dashboards. Don't assume both if the user only wants one.
7. **Notification channel.** Ask which tool (Slack, MS Teams, email, other) and confirm the CI secret/variable name that will hold the webhook/credential — never its actual value.
8. **Nightly-regression schedule.** Confirm the cron expression/time the scheduled pipeline should run on.
9. **History retention for `flaky-test-triage`.** Confirm whether this project wants cross-run history persisted in `reports/history/` (default: yes — it's the only thing that makes `flaky-test-triage`'s cross-run flakiness detection reachable at all; without it, that skill is limited to within-run retry detection forever) and, if so, how many recent runs to retain (default 20, to bound growth). A fresh CI checkout has nothing on disk from prior runs, so this also means confirming which of the platform's own persistent-cache/artifact-store mechanisms will carry `reports/history/` from one pipeline run to the next. If the user declines, record that explicitly rather than silently wiring it anyway.

Don't proceed past this step on assumptions where the answer changes what gets written to the pipeline file.

## Planned additions

Present this as a plan before editing anything, filled in with the real, confirmed values from Step 0 — not placeholders:

| Trigger | Scope (marker) | Environment(s) | Parallelization | Retries | Report formats | Notifies on failure |
|---|---|---|---|---|---|---|
| Pull request | `smoke` | `<confirmed env, e.g. dev>` | `<N>` workers, shard by file | `<confirmed reruns/delay, or "none">` | `<confirmed formats>` | `<confirmed channel>` |
| Scheduled (nightly) | `regression` | `<all confirmed envs>` | `<N>` workers, shard by file | `<confirmed reruns/delay, or "none">` | `<confirmed formats>` | `<confirmed channel>` |

## Build phases

Create these in order. For each phase, state what/why/where/how in conversation *before* editing files, then make just that phase's change before moving on.

1. **Marker registration** — add/confirm `smoke`/`regression` (or the project's chosen names) in `pytest.ini`'s `markers =` section (or `pyproject.toml`'s equivalent). Cross-check every generated test file under `tests/` has at least one of these markers applied; list any that don't as an Open Question rather than silently excluding them from both pipeline scopes.
   *Why:* the pipeline needs a mechanical way to select "just smoke" vs. "everything" — `-m smoke` / `-m regression` is that mechanism.

2. **Parallelization wiring** — add the confirmed tool (`pytest-xdist` by default) to the dependency file, and wire the confirmed worker count/shard strategy into the pytest invocation (e.g. `pytest -n <N> --dist loadscope` to keep same-file tests on one worker, matching the isolation guardrail).
   *Why:* cuts wall-clock time on both the PR-smoke gate and the nightly-regression run. *How it connects:* every pipeline stage below invokes pytest through this same flag set, not a bespoke one per stage.

3. **Retry wiring** — if Step 0 confirmed a retry policy, add `pytest-rerunfailures` to the dependency file and append the confirmed `--reruns <N> --reruns-delay <S>` flags to the same pytest invocation from phase 2. If the user declined retries, skip this phase and say so rather than leaving it ambiguous.
   *Why:* absorbs transient infra noise (a slow environment, a dropped connection) without a human re-triggering the whole pipeline by hand. *How it connects:* same invocation flag set as phase 2 — one pytest command, not a separate retry stage.

4. **Report format wiring** — for each format confirmed in Step 0 beyond the Allure results `pytest.ini` already produces, append the matching flag to the pytest invocation (e.g. `--junitxml=reports/junit.xml`).
   *Why:* CI-native dashboards and downstream tooling (test-result trend graphs, PR status checks) typically read JUnit XML, not raw Allure JSON. *How it connects:* feeds phase 7's artifact publishing and, for JUnit, is a direct input `create-report`'s `junit` format can already parse.

5. **Environment matrix** — wire the pipeline definitions so the PR-triggered stage runs `-m smoke --env <confirmed dev/staging env>` and the scheduled stage runs `-m regression`, once per confirmed environment (as separate parallel steps if the platform supports it, sequential otherwise — confirm which with the user if it matters for this project).
   *Why:* a PR shouldn't wait on the full environment sweep; a merged/nightly build should catch environment-specific regressions the smoke pass wouldn't.

6. **Failure notifications** — add a step, gated on pipeline/stage failure (the confirmed platform's native failure-hook, e.g. Bitbucket's `after-script` combined with a `$BITBUCKET_EXIT_CODE` check, or an `on: failure` job in other platforms), that posts a summary — pass/fail counts, and breaking `context/schema-validation-report.md` findings if that file exists — to the confirmed channel via the confirmed secret variable name.
   *Why:* a red pipeline nobody looks at is no better than no pipeline. *How it connects:* reads the same artifacts `create-report` would use, but only to build the notification summary — it doesn't replace `create-report`'s own output.

7. **Artifact/report publishing** — ensure the pipeline uploads whatever `pytest-api`'s validation phase or `create-report` produce — Allure results, the JUnit XML from phase 4 if generated, `reports/` generally — as CI build artifacts, so a failure is debuggable from the CI run itself, not just from a one-line notification.
   *Why:* the notification says *that* something broke; the published artifact is what lets someone see *what* broke without re-running locally.

8. **History archiving (for `flaky-test-triage`)** — if Step 0 confirmed history retention, wire the pipeline to: (a) restore the previous `reports/history/` contents at the start of the test stage, before `pytest` runs, from the confirmed CI-native persistent-cache/artifact-store mechanism — a fresh checkout otherwise has nothing on disk from prior runs; (b) immediately after execution, copy that run's deduplicated Allure/JUnit summary (a compact per-test outcome record, not the full raw results directory, to bound size) into `reports/history/<run-id-or-timestamp>/`, pruning entries beyond the confirmed retention count; (c) save the updated `reports/history/` back under the same cache key so the *next* run inherits it. If the user declined history retention in Step 0, skip this phase and say so rather than leaving it ambiguous.
   *Why:* `flaky-test-triage`'s cross-run detection needs archived prior-run outcomes to compare against, and nothing else in this suite ever populates `reports/history/` — without this phase, that skill's cross-run capability is permanently unreachable no matter how many times the pipeline runs, not just temporarily thin on data. *How it connects:* consumed entirely by `flaky-test-triage`, a sibling skill this one never invokes directly — this phase only makes the data available, it never analyzes it for flaky patterns itself.

## Limitations

This skill is only responsible for CI wiring. It must **not**:

- Generate test cases or test scripts (that's `api-test-design`/`pytest-api`).
- Validate schemas or interpret API responses (that's `pytest-api`'s validation phase).
- Produce the human-facing test report itself (that's `create-report`) — this skill only makes sure that output gets published/notified, not regenerate it.
- Decide whether a test is flaky or quarantine one (that's `flaky-test-triage`, working from run history after the fact) — this skill's retry wiring only absorbs transient failures within a single run. This skill's history-archiving phase populates the `reports/history/` data that skill reads; it never analyzes that history for flaky patterns itself.
- Invent a webhook URL, API key, environment base URL, retry count, or notification tool the user hasn't named.
- Trigger or execute a CI run itself — it edits config; the confirmed platform runs it when the corresponding event (PR, schedule, push) actually fires.

If asked to do any of the above mid-conversation, say which skill owns that responsibility instead of doing it here.

## Notes for reuse across projects

- Never hardcode a project's actual webhook URL, environment base URL, or CI platform choice in this skill file itself — Step 0's confirmation and disk detection are what stay generic across every project.
- If the project's CI platform isn't Bitbucket, build the equivalent constructs (matrix/parallel jobs, scheduled triggers, secret references) in that platform's own idiom rather than forcing a Bitbucket-shaped translation onto it.
- Once confirmed for a project, the marker vocabulary (`smoke`/`regression` or its chosen equivalent) is fixed for that project — don't let a later run introduce a third, uncoordinated label.
- Re-running this skill to add one new environment or notification channel only needs that addition confirmed, not the whole pipeline re-confirmed from scratch.
