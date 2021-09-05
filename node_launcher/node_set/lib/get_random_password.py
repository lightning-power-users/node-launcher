import secrets


def get_random_password() -> str:
    return secrets.token_hex()
