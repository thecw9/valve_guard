import jwt


def generate_token(username: str, secret_key: str) -> str:
    payload = {"username": username}
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token
