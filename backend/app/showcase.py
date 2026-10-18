"""Public presentation metadata; demo credentials are opt-in and local only."""

import json
import os
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select, delete
from .db import ROOT
from .models import User, LoginSession


def welcome(db):
    data = json.loads((ROOT / "data/showcase.json").read_text(encoding="utf-8"))
    data["login"] = None
    path = ROOT / "runtime/showcase-login.json"
    if os.getenv("APP_ENV", "local") == "local" and path.exists():
        credentials = json.loads(path.read_text(encoding="utf-8"))
        user = db.scalar(select(User).where(User.username == credentials["username"]))
        try:
            if user and PasswordHasher().verify(
                user.password_hash, credentials["password"]
            ):
                data["login"] = credentials
        except VerificationError:
            pass
    return data


def configure_demo_login(db, previous, username, password):
    if os.getenv("APP_ENV", "local") != "local":
        raise ValueError("Public demo login setup is local-only")
    user = db.scalar(select(User).where(User.username == previous))
    if not user or not username.strip() or not password:
        raise ValueError("Existing reviewer and nonempty credentials required")
    other = db.scalar(select(User).where(User.username == username, User.id != user.id))
    if other:
        raise ValueError("Target username already belongs to another reviewer")
    user.username = username
    user.password_hash = PasswordHasher().hash(password)
    db.execute(delete(LoginSession).where(LoginSession.user_id == user.id))
    db.commit()
    # This is intentionally public demo access, never an API or production secret.
    (ROOT / "runtime/showcase-login.json").write_text(
        json.dumps(dict(username=username, password=password)), encoding="utf-8"
    )
    (ROOT / "runtime/local-account.txt").write_text(
        f"Username: {username}\nPassword: {password}\n", encoding="utf-8"
    )
