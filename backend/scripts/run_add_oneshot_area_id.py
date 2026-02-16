"""
Añade la columna area_id (nullable) a la tabla one_shot_tasks.
One shot = area_id NULL; si tiene valor, la tarea está ligada a ese área.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine

SQL = """
ALTER TABLE one_shot_tasks
ADD COLUMN IF NOT EXISTS area_id INTEGER NULL
REFERENCES areas(id) ON DELETE SET NULL;
"""
INDEX = "CREATE INDEX IF NOT EXISTS ix_one_shot_tasks_area_id ON one_shot_tasks (area_id);"

if __name__ == "__main__":
    with engine.connect() as conn:
        conn.execute(text(SQL))
        conn.execute(text(INDEX))
        conn.commit()
    print("Columna one_shot_tasks.area_id añadida (o ya existía).")
