import json
from argon2 import PasswordHasher
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import pytest
from backend.app.db import Base
from backend.app.models import User, LoginSession, now
from backend.app import showcase


def test_public_demo_configuration_preserves_account_and_gates_disclosure(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(showcase, "ROOT", tmp_path)
    monkeypatch.setenv("APP_ENV", "local")
    (tmp_path / "data").mkdir()
    (tmp_path / "runtime").mkdir()
    (tmp_path / "data/showcase.json").write_text(
        json.dumps({"team": {"en": "Demo"}, "creators": []})
    )
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(
            username="old", password_hash=PasswordHasher().hash("previous-secret")
        )
        db.add(user)
        db.flush()
        original_id = user.id
        db.add(
            LoginSession(
                user_id=user.id,
                token_hash="old-session",
                csrf="old-csrf",
                expires=now(),
            )
        )
        db.commit()
        assert showcase.welcome(db)["login"] is None
        showcase.configure_demo_login(db, "old", "new", "12345")
        assert db.get(User, original_id).username == "new"
        assert db.scalar(select(LoginSession)) is None
        assert PasswordHasher().verify(db.get(User, original_id).password_hash, "12345")
        assert showcase.welcome(db)["login"] == {"username": "new", "password": "12345"}
        monkeypatch.setenv("APP_ENV", "production")
        assert showcase.welcome(db)["login"] is None
        with pytest.raises(ValueError, match="local-only"):
            showcase.configure_demo_login(db, "new", "other", "password")
        monkeypatch.setenv("APP_ENV", "local")
        user.password_hash = PasswordHasher().hash("changed-elsewhere")
        db.commit()
        assert showcase.welcome(db)["login"] is None
    engine.dispose()
