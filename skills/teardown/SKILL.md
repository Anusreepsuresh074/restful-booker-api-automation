---
name: teardown
description: Clears stale test data from a completed pytest-api validation run. Reads the runtime created-resource registry pytest-api's suite maintains (e.g. reports/created-resources.jsonl), resolves each resource type's delete endpoint from context/api-context.md, works out safe deletion order for dependent resources, and deletes only entries created before today — never same-day entries, so today's data stays available for debugging the run that just happened. Never invents a resource type, endpoint, or auth flow; only clears what the registry says the suite actually created. Only ever runs after the calling agent (or the user directly) has asked "Run teardown to clear stale test data from before today? (y/n)" and gotten an explicit yes. Use right after pytest-api's validation phase has finished executing the suite.
---

# Teardown

Clears out stale test data left behind by prior runs: for every resource type recorded in the runtime created-resource registry with a creation timestamp **before today**, this skill resolves the real delete endpoint, works out the order dependent resources must be removed in, and calls it directly against the target environment. Entries created **today are left alone** — same-day data (including whatever the run that just finished created) stays in the environment in case a failing test needs to be debugged against it. It never writes a test method or fixture code, never invents an endpoint that isn't in `context/api-context.md`, and never runs without the user having explicitly said yes to a direct "run teardown now?" confirmation.

**Workflow position:** step 6 — runs after `pytest-api` has executed the generated suite (step 5's validation phase), gated on the user confirming they want stale test data cleared. `context/schema-validation-report.md` and `create-report`'s downstream report are both already captured before teardown deletes anything, so clearing data afterward never affects report accuracy. Because only prior-day entries are eligible, running teardown right after a `pytest-api` validation pass never touches what that same pass just created.

## When to use

- Right after `pytest-api`'s validation phase finishes executing a suite that created one or more resources, **and** the user has answered yes to "Run teardown to clear stale test data (created before today)?"
- Periodically (e.g. once a day, or before a new test run) to clear out resources created on prior days.
- Someone asks "clear out the test data from before today" or "why is test data piling up in `<environment>`?"
- Never run proactively or as an automatic follow-on to `pytest-api` — the confirmation is a hard gate, not a formality.

## Prerequisites (hard stop if missing)

| Input | Source skill | Required? |
|---|---|---|
| Explicit user "yes" to running teardown now | Human (or the calling agent's confirmation step) | **Yes** — if not yet asked/answered, ask `Run teardown to clear stale test data (created before today)? (y/n)` and stop until answered |
| Runtime created-resource registry (e.g. `reports/created-resources.jsonl`) with one or more entries | `pytest-api` (populated by its own validation phase, which just executed the suite) | **Yes** — if empty or missing, say `Nothing to clear — no tracked test data found.` and stop |
| `context/api-context.md` | `get-context` | **Yes** — needed to resolve each resource type's delete endpoint |
| Auth fixture / token flow | `get-api-auth` + existing `conftest.py` | **Yes** — teardown's delete calls reuse the same auth the create calls used |

## Downstream handoff (nothing here is re-derived downstream)

Nothing in the core sequence re-checks teardown's own logic — `create-report` reports on the run `pytest-api`'s validation phase already captured, independent of whether teardown has cleared the underlying stale data yet. If a delete call itself throws unexpectedly (not a 404/410), that's a teardown failure to surface directly to the user, not something a downstream skill re-implements.

## Guardrails

These are hard constraints, not style preferences. If a step below seems to conflict with one of these, the guardrail wins.

- **Never run without an explicit yes.** This is the hard gate step 6 exists behind: ask (or confirm the calling agent already asked) `Run teardown to clear stale test data (created before today)? (y/n)` and stop on anything other than an affirmative answer. This is separate from — and in addition to — confirming which environment, per the destructive-action guardrail below.
- **Never touch today's entries.** Compare each registry entry's recorded creation timestamp against the current date (in the environment/project's reference timezone — confirm which one rather than assuming UTC). If it was created today, skip it: don't delete it, don't mark it, leave it in the registry untouched. This is the point of the skill — same-day data must stay available for debugging a run that just happened. Only entries created on a prior day are eligible for deletion, even when the user's "yes" sounded like "clear everything."
- **Read-only on everything except the registry and its own notes file.** Never modify `context/api-context.md`, `context/test-case-matrix.md`, test methods, fixture code, or endpoint/payload/schema files. The only things this skill writes are: entries in the runtime created-resource registry (marking stale ones cleared once deleted) and its own `context/teardown-notes.md`.
- **No fabrication.** Only call a delete endpoint for a resource type actually documented in `context/api-context.md`'s endpoint inventory. If no delete endpoint is documented for a resource type the registry says the suite created, say so explicitly under Open Questions in `context/teardown-notes.md` — never invent one, and never silently drop cleanup for it either.
- **Deletion order matters.** If resource A depends on resource B (created together, or A references B), delete in reverse-dependency order. Document the reasoning only when it's non-obvious — don't caption every line.
- **Idempotent teardown.** A delete call must not fail the run if the resource is already gone (e.g. a delete-endpoint test already removed it, or a previous teardown run partially completed). Classify a `404`/`410`-class response as "already gone" and continue; treat every other error class as a genuine teardown failure and surface it — never swallow those silently.
- **No automatic wiring into the test session.** Never add post-yield deletion, a finalizer, or an autouse fixture that deletes resources as part of running the suite — that would delete same-day data the moment it's created, defeating the whole point of this skill. Teardown always runs as its own explicit, confirmed pass over the persisted registry, invoked separately from `pytest` itself.
- **Executing deletes against a live API is a destructive action.** Same as `pytest-api`'s validation-phase execution guardrail: confirm which environment first, and never run against production without the user explicitly naming it and approving that. This is on top of, not instead of, the yes/no gate above. **Never inherit the environment silently from "whatever `pytest-api` last ran"** — that only holds when a `pytest-api` run actually happened earlier in this same conversation; for a standalone/periodic invocation (this skill's own "When to use" explicitly allows one), ask which environment(s) to target per Step 2, using the registry's own recorded environment values as the choices to present, rather than picking one on the user's behalf.
- **No credentials in output.** Reuse whatever auth fixture `get-api-auth` documented and `pytest-api` already wired for the create calls — never hardcode or print a token, key, or password.
- **Closed vocabulary for how each resource's cleanup was resolved.** Use exactly one of: `documented-delete-endpoint`, `cascade-via-parent`, `no-delete-endpoint-available`. Don't invent other labels.
- **Only clear resources the registry says the suite actually created.** Every resource type touched must trace back to an actual entry in the created-resource registry — never speculative cleanup for a resource type not recorded there.
- **Idempotent re-runs.** Re-running teardown only acts on registry entries not already marked cleared (and still eligible by age) — it must not attempt to re-delete (or double-count) an entry a prior teardown run already cleared, and must not re-derive the whole registry from scratch.

## Steps

1. **Confirm the go-ahead.** If the calling agent hasn't already asked and recorded a yes in this conversation, ask directly: `Run teardown to clear stale test data (created before today)? (y/n)`. Stop here on anything other than an explicit yes.
2. **Determine the target environment(s) explicitly — never inherit one silently.**
   - If `pytest-api`'s validation phase ran earlier in **this same conversation**, its target environment is the default — but still name it back to the user as part of the go-ahead/environment confirmation (per the destructive-action guardrail below), don't just assume silent agreement.
   - Otherwise (a standalone or periodic invocation, per this skill's own "When to use" — there's no same-session run to inherit from): read the registry first (Step 3) far enough to list the **distinct environment values already present** across its entries, present that list, and ask the user which environment(s) to target this run — "all of them" is a valid, explicit answer, but it must be given, not assumed. Don't default to guessing a single environment when the registry holds more than one and nobody's said which to clean.
   - This matters because a registry can accumulate entries from environments the project doesn't run `pytest-api` against every time — without an explicit choice here, those entries would never become eligible for cleanup at all, since nothing else in this skill scopes to them otherwise.
3. **Read the runtime registry.** Load the created-resource registry `pytest-api` populates (e.g. `reports/created-resources.jsonl`) and filter to entries not yet marked cleared, for the environment(s) confirmed in Step 2.
4. **Partition by age.** Compare each entry's creation timestamp against today's date. Entries created today are left untouched — don't include them in any deletion pass, don't mark them. Entries created on a prior day are candidates for cleanup.
5. **Resolve each stale resource type's delete endpoint.** Cross-reference `context/api-context.md`'s endpoint inventory for a `DELETE` (or equivalent) operation on that resource. Classify the resolution using the closed vocabulary above:
   - `documented-delete-endpoint` — a DELETE endpoint for this exact resource is in the inventory.
   - `cascade-via-parent` — no direct delete endpoint, but deleting a parent resource is documented to cascade-remove this one; cite the parent's delete endpoint instead.
   - `no-delete-endpoint-available` — neither exists; flag under Open Questions rather than fabricating one.
6. **Determine deletion order.** Where multiple stale resource types were created together (e.g. a child resource created under a parent id), order deletes so dependents go before their parents.
7. **Confirm the target environment(s)** one final time per the destructive-action guardrail (a restatement of Step 2's choice, not a new question), then execute the deletes: for each stale registry entry with a resolvable endpoint, call it through the project's `ApiBase`/helper layer (never raw `requests`/`httpx`) in the order from Step 6, and classify the response — already-gone vs genuine failure — per the idempotency guardrail.
8. **Mark cleared entries in the registry** so a re-run doesn't attempt to delete them again. Leave `no-delete-endpoint-available` entries untouched in the registry (don't fake a clear) and record them under Open Questions. Never touch today's entries in this step.
9. **Emit `context/teardown-notes.md`** using the template below, and print a short summary in conversation: what was cleared, what failed, what's still open, and how many today-created entries were intentionally left alone.
10. **Report and hand off.** Tell the user what was cleared (or partially cleared, listing gaps and genuine failures) — teardown is the last step before `create-report`, which reports on the run independent of whether cleanup happened.

## Output

No test/framework code is touched (unless the project has no registry read/delete helper yet, in which case add a minimal one, e.g. `src/helper/teardown_helper.py`, following `pytest-api`'s existing layout convention). This skill writes only:
- Live DELETE calls against the resolved endpoints for stale (prior-day) registry entries.
- Updates to the runtime created-resource registry (marking stale entries cleared; today's entries untouched).
- `context/teardown-notes.md`.

`context/teardown-notes.md`:

```markdown
# Teardown Notes

_Generated by teardown on <date>, clearing stale (pre-today) test data against <environment>. Today's entries are intentionally left in place for debugging. Re-run any time you want another day's worth of prior data cleared._

## Resource cleanup resolution

| Resource type | Created on | Registry entries cleared | Delete endpoint | Resolution | Deletion order | Notes |
|---|---|---|---|---|---|---|
| <e.g. widget> | <date, prior day> | 3 | `DELETE /widgets/{id}` | documented-delete-endpoint | 1 (no dependents) | |

## Today's entries (left in place)

| Resource type | Count | Notes |
|---|---|---|
| <e.g. widget> | <n> | retained for debugging today's run |

## Open questions / follow-ups

- <resource types with no resolvable delete endpoint, genuine (non-404/410) delete failures, ambiguous dependency ordering — or "none">
```

## Bias to counter

Models tend to (a) delete everything in the registry regardless of creation date, wiping out the very same-day data a human might need to debug a just-finished run, (b) skip teardown entirely for a resource type with no obvious delete endpoint, leaving it silently orphaned with no Open Questions entry, (c) write a fire-and-forget delete wrapped in a broad `except` that also swallows real failures, (d) run without waiting for an explicit yes because "it's obviously fine to clean up," or (e) assume the environment to target is whatever `pytest-api` most recently ran against, even on a standalone/periodic invocation with no such run this conversation — which leaves any environment the project doesn't happen to re-test against perpetually unreachable for cleanup, quietly accumulating stale data forever. Force the age check for (a) on every run — never let "clean everything" collapse today's entries into the deletion set, even when the user's yes sounded unconditional. Force an explicit Open Questions entry for (b), distinct already-gone-vs-genuine-failure handling for (c) — a bare `except: pass` around a delete call is never acceptable — a hard stop for (d) even when running teardown seems like the obviously-correct next move, and an explicit environment question for (e) per Step 2 whenever there's no same-session run to inherit from.

## Notes for reuse across projects

- Never hardcode a project-specific resource type, endpoint, or dependency chain in this skill file itself — always resolve fresh from that project's `context/api-context.md` and the actual registry entries a run produced.
- Which resources need `cascade-via-parent` handling varies per API — don't assume last project's cascade behavior applies here.
- "Today" means the project's reference timezone/environment clock, not the machine running this skill — confirm which one the registry's timestamps use before comparing dates, rather than assuming UTC.
- If a project has many stale resource types, still wire all resolvable ones in the same run; only truncate what's printed inline in conversation (and say so).
