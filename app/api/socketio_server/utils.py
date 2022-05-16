from typing import Optional

import jwt


def get_token_from_environ(environ: dict) -> Optional[str]:
    token = environ.get("HTTP_AUTHORIZATION")
    if not token:
        return
    return token


def get_profile_id_from_token(token: str) -> Optional[str]:
    try:
        user_data = jwt.decode(token, options={"verify_signature": False})
    except jwt.DecodeError:
        return

    if profile_id := user_data.get("current_profile_id"):
        return profile_id
    return
