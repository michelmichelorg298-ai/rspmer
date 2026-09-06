"""Réinitialise les tables pour aligner la base avec les modèles SQLAlchemy."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.services.user_service import ensure_default_users


def reset_database(only_users: bool = False) -> None:
    is_sqlite = engine.url.drivername.startswith("sqlite")
    cascade = "" if is_sqlite else " CASCADE"
    with engine.connect() as conn:
        if only_users:
            conn.execute(text(f"DROP TABLE IF EXISTS users{cascade}"))
        else:
            conn.execute(text(f"DROP TABLE IF EXISTS depences{cascade}"))
            conn.execute(text(f"DROP TABLE IF EXISTS users{cascade}"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        ensure_default_users(db)
    finally:
        db.close()

    print("Base réinitialisée avec succès.")
    print("Comptes créés : reader@gmail.com, writer@gmail.com, admin@gmail.com")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Réinitialiser la base de données")
    parser.add_argument(
        "--only-users",
        action="store_true",
        help="Ne réinitialiser que la table users (conserve les dépenses)",
    )
    args = parser.parse_args()
    reset_database(only_users=args.only_users)
