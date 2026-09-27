BOOKING_DATES_SCHEMA = {
    "type": "object",
    "properties": {
        "checkin": {"type": "string"},
        "checkout": {"type": "string"},
    },
    "required": ["checkin", "checkout"],
    "additionalProperties": False,
}

BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "integer"},
        "depositpaid": {"type": "boolean"},
        "bookingdates": BOOKING_DATES_SCHEMA,
        "additionalneeds": {"type": "string"},
    },
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "additionalProperties": False,
}

BOOKING_ID_LIST_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "bookingid": {"type": "integer"},
    },
    "required": ["bookingid"],
    "additionalProperties": False,
}

BOOKING_ID_LIST_SCHEMA = {
    "type": "array",
    "items": BOOKING_ID_LIST_ITEM_SCHEMA,
}

CREATE_BOOKING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "bookingid": {"type": "integer"},
        "booking": BOOKING_SCHEMA,
    },
    "required": ["bookingid", "booking"],
    "additionalProperties": False,
}
