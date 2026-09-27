# Payloads

`<feature>_payload.py` — request-body factories for each feature. Every factory returns a plain
dict (never a side effect), built with unique values per call (see `booking_payload_unique`) so
tests never collide with data left behind by another run on this shared instance.
