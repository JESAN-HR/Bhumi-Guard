"""Explicit local-only public demo login setup; preserves reviewer ID and cases."""

import argparse
import getpass
from backend.app.db import Session
from backend.app.showcase import configure_demo_login

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", required=True)
    parser.add_argument("--username", required=True)
    args = parser.parse_args()
    with Session() as db:
        configure_demo_login(
            db, args.previous, args.username, getpass.getpass("Public demo password: ")
        )
    print("Local demo login updated; previous sessions revoked and cases preserved.")
