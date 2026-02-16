"""
Migración única que deja el esquema de la BD al día.
- Crea las tablas si no existen (users, areas, projects) con todas las columnas.
- Añade columnas que falten en BDs antiguas (p. ej. areas.color, projects.icon).

Idempotente: se puede ejecutar en cada arranque (docker compose up).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine

# 1) Tablas completas (si no existen)
SQL_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS areas (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        description VARCHAR(1000),
        color VARCHAR(7),
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        area_id INTEGER NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
        icon VARCHAR(20),
        name VARCHAR(255) NOT NULL,
        description VARCHAR(1000),
        pinned BOOLEAN NOT NULL DEFAULT false,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS one_shot_tasks (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title VARCHAR(500) NOT NULL,
        done BOOLEAN NOT NULL DEFAULT false,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """,
]

# 2) Índices (por si la tabla se creó sin ellos)
SQL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_areas_user_id ON areas (user_id);",
    "CREATE INDEX IF NOT EXISTS ix_projects_area_id ON projects (area_id);",
    "CREATE INDEX IF NOT EXISTS ix_one_shot_tasks_user_id ON one_shot_tasks (user_id);",
]

# 3) Columnas añadidas después (BDs que ya tenían las tablas sin estas columnas)
SQL_ALTERS = [
    "ALTER TABLE areas ADD COLUMN IF NOT EXISTS color VARCHAR(7) NULL;",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS icon VARCHAR(20) NULL;",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS pinned BOOLEAN NOT NULL DEFAULT false;",
]


def run():
    with engine.connect() as conn:
        for sql in SQL_TABLES:
            conn.execute(text(sql))
        for sql in SQL_INDEXES:
            conn.execute(text(sql))
        for sql in SQL_ALTERS:
            conn.execute(text(sql))
        conn.commit()
    print("Migraciones aplicadas (esquema al día).")


if __name__ == "__main__":
    run()
