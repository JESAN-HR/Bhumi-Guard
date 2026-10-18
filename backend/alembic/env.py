from alembic import context
from backend.app.db import Base, engine
from backend.app import models


def run():
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=Base.metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


run()
