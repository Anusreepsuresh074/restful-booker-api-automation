# Endpoints

`<feature>_ep.py` — path constants for each feature's endpoints, e.g. `BOOKING_BY_ID = "/booking/{id}"`.
Every helper method builds its URL from one of these instead of a string literal, so an endpoint
path only ever needs to change in one place.
