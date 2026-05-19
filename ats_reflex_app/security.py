from __future__ import annotations

import hashlib
import hmac
import os
from base64 import urlsafe_b64encode, urlsafe_b64decode

_ITERATIONS = 120_000


def _b64e(data: bytes) -> str:
    return urlsafe_b64encode(data).decode("utf-8")


def _b64d(data: str) -> bytes:
    return urlsafe_b64decode(data.encode("utf-8"))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${_b64e(salt)}${_b64e(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            _b64d(salt),
            int(iterations),
        )
        return hmac.compare_digest(_b64e(digest), expected)
    except Exception:
        return False
