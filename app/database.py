"""Connection to the SQLite database via SQLModel.
At startup, the .sql files of the db folder are executed in alphabetical order,
except those already listed in the tracking file (executed_sql.txt)
"""

import sqlite3
from pathlib import Path
from sqlalchemy import event
from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database.db"
SQL_DIR = BASE_DIR.parent / "db"
TRACK_PATH = BASE_DIR / "executed_sql.txt"

def init_db():
    """Executes the .sql files that are not in the tracking file yet."""
    files = sorted(SQL_DIR.glob("*.sql"))   #sort by file name order
    if not files:
        raise FileNotFoundError(f"No .sql file found in {SQL_DIR}")

    is_new = not DB_PATH.exists()
    if is_new:
        TRACK_PATH.unlink(missing_ok=True)

    executed = set()
    if TRACK_PATH.exists():
        lines = TRACK_PATH.read_text(encoding="utf-8").splitlines()
        executed = {line.strip() for line in lines if line.strip()}

    conn = sqlite3.connect(DB_PATH)
    try:
        for file in files:
            if file.name in executed:
                continue
            conn.executescript(file.read_text(encoding="utf-8"))
            with open(TRACK_PATH, "a", encoding="utf-8") as track:
                track.write(file.name + "\n")
    except Exception:
        conn.close()
        if is_new:
            DB_PATH.unlink(missing_ok=True)      #to avoid leaving a half-created database
            TRACK_PATH.unlink(missing_ok=True)
        raise                                    #an existing database is never deleted
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
