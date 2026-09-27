import uuid


def unique_name(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def booking_payload(**overrides) -> dict:
    payload = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-05",
        },
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload


def booking_payload_unique(**overrides) -> dict:
    payload = booking_payload(firstname=unique_name("Fn"), lastname=unique_name("Ln"))
    payload.update(overrides)
    return payload


def booking_partial_update_payload(**overrides) -> dict:
    payload = {"firstname": unique_name("Updated")}
    payload.update(overrides)
    return payload
