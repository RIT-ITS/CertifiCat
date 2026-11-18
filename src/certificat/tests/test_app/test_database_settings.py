import sqlite3
from contextlib import closing

import peewee

from certificat.settings.dynamic import SQLiteDatabaseSettings


def test_sqlite_to_peewee_uses_the_django_database(tmp_path):
    path = str(tmp_path / "certificat.sqlite3")
    settings = SQLiteDatabaseSettings(name=path)

    db = settings.to_peewee()

    assert isinstance(db, peewee.SqliteDatabase)
    assert db.database == settings.to_backend()["NAME"] == path


def test_sqlite_to_peewee_uses_the_django_timeout(tmp_path):
    path = str(tmp_path / "certificat.sqlite3")

    assert SQLiteDatabaseSettings(name=path).to_peewee()._timeout == 5
    assert (
        SQLiteDatabaseSettings(name=path, options={"timeout": 20}).to_peewee()._timeout
        == 20
    )


def test_sqlite_to_peewee_tables_are_visible_to_django(tmp_path):
    # Huey stats creates huey_event through peewee, and Django's unmanaged
    # HueyEvent model has to find it in its own database.
    path = str(tmp_path / "certificat.sqlite3")
    db = SQLiteDatabaseSettings(name=path).to_peewee()

    with db:
        db.execute_sql("CREATE TABLE huey_event (id INTEGER PRIMARY KEY)")

    with closing(sqlite3.connect(path)) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    assert "huey_event" in tables
