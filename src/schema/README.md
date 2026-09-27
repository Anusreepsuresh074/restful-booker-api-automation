# Schema

`<feature>_schema.py` — response schemas for each feature, resolved from `context/api-context.md`.
Each is a plain JSON Schema dict consumed by `AssertHelper.assert_schema` inside the matching
helper — the same resolved definition used both when a test runs and when
`context/schema-validation-report.md` was generated, so the two never disagree.
