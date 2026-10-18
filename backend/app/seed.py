import argparse, json, os, getpass
from sqlalchemy import select
from argon2 import PasswordHasher
from .db import Session, ROOT, Base, engine
from .models import User, Location, Party, ReviewCase
from .fixtures import scenarios
from .services import new_case


from .geography import import_locations


def seed(username, password, location_file=None):
    with Session() as db:
        import_locations(db, location_file or ROOT / "data/locations/locations.json")
        for pid, en, bn in [
            ("DEMO-PARTY-A", "Demo Seller A", "ডেমো বিক্রেতা ক"),
            ("DEMO-PARTY-B", "Demo Seller B", "ডেমো বিক্রেতা খ"),
        ]:
            if not db.get(Party, pid):
                db.add(Party(id=pid, label_en=en, label_bn=bn))
        user = db.scalar(select(User).where(User.username == username))
        if not user:
            if len(password) < 12:
                raise ValueError("Use a password of at least 12 characters")
            user = User(
                username=username, password_hash=PasswordHasher().hash(password)
            )
            db.add(user)
        db.commit()
        for s in scenarios():
            if not db.scalar(
                select(ReviewCase).where(
                    ReviewCase.owner_id == user.id, ReviewCase.scenario_id == s["id"]
                )
            ):
                new_case(db, user, s["id"], s["fields"]["mouza_id"])
    (ROOT / "data/scenarios/cases.json").write_text(
        json.dumps(scenarios(), ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--username", default=os.getenv("DEMO_USERNAME", "reviewer"))
    p.add_argument("--reset", action="store_true")
    p.add_argument("--confirm")
    p.add_argument("--locations", type=lambda x: __import__("pathlib").Path(x))
    a = p.parse_args()
    if a.reset:
        if (
            os.getenv("APP_ENV", "local") != "local"
            or a.confirm != "DELETE-FICTIONAL-DEMO"
        ):
            raise SystemExit(
                "Reset requires local mode and --confirm DELETE-FICTIONAL-DEMO"
            )
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    password = os.getenv("DEMO_PASSWORD") or getpass.getpass(
        "New local demo password (12+ characters): "
    )
    seed(a.username, password, a.locations)
    print("Seeded 22 fictional scenarios. Existing users and cases preserved.")
