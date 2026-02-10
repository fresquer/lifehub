"""
Añade la columna icon a la tabla projects.
Usa la misma DATABASE_URL que el backend.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine

SQL = "ALTER TABLE projects ADD COLUMN IF NOT EXISTS icon VARCHAR(20) NULL;"

if __name__ == "__main__":
    with engine.connect() as conn:
        conn.execute(text(SQL))
        conn.commit()
    print("Columna projects.icon añadida (o ya existía).")
