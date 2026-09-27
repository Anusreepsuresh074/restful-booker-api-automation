import os


def auth_payload(username: str = None, password: str = None) -> dict:
    return {
        "username": username or os.environ["AUTH_USERNAME"],
        "password": password or os.environ["AUTH_PASSWORD"],
    }


def auth_payload_missing_password(username: str = None) -> dict:
    return {
        "username": username or os.environ["AUTH_USERNAME"],
    }


def auth_payload_wrong_credentials() -> dict:
    return {
        "username": "not-a-real-user",
        "password": "not-the-real-password",
    }
