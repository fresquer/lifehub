"""
Añade la columna color a la tabla areas.
Usa la misma DATABASE_URL que el backend (ej. desde run_dev.bat o con .env).
"""
import sys
from pathlib import Path

# Permitir importar app desde la raíz del backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine

SQL = "ALTER TABLE areas ADD COLUMN IF NOT EXISTS color VARCHAR(7) NULL;"

if __name__ == "__main__":
    with engine.connect() as conn:
        conn.execute(text(SQL))
        conn.commit()
    print("Columna areas.color añadida (o ya existía).")
