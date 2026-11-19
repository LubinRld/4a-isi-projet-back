"""Connection to the SQLite database via SQLModel.
If the database file does not exist, it is created at startup by running
all the .sql files in the sql/ folder, in alphabetical order
"""

import sqlite3
from pathlib import Path
from sqlalchemy import event
from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database.db"
SQL_DIR = BASE_DIR.parent / "db"

def init_db():
    """Creates the database from the .sql files if it does not exist yet."""
    if DB_PATH.exists():
        return

    files = sorted(SQL_DIR.glob("*.sql"))   #sort by file name order
    if not files:
        raise FileNotFoundError(f"No .sql file found in {SQL_DIR}")

    conn = sqlite3.connect(DB_PATH)
    try:
        for file in files:
            conn.executescript(file.read_text(encoding="utf-8"))
    except Exception:
        conn.close()
        DB_PATH.unlink(missing_ok=True)        #to avoid leaving a half-created database
        raise
    conn.close()


init_db()

engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def activate_foreign_key(dbapi_connection, _):
    #The PRAGMA is specific to each connection: we enable it every time one is opened
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def get_session():
    
    with Session(engine) as session:
        yield session