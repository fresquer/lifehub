"""
Crea la tabla project_next_actions, migra datos desde projects.next_action
y elimina la columna next_action de projects. Idempotente.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text, inspect
from app.database import engine

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS project_next_actions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
"""
INDEX = "CREATE INDEX IF NOT EXISTS ix_project_next_actions_project_id ON project_next_actions (project_id);"

MIGRATE_DATA = """
INSERT INTO project_next_actions (project_id, title, done)
SELECT id, TRIM(next_action), false
FROM projects
WHERE next_action IS NOT NULL AND TRIM(next_action) <> '';
"""
DROP_COLUMN = "ALTER TABLE projects DROP COLUMN IF EXISTS next_action;"


if __name__ == "__main__":
    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE))
        conn.execute(text(INDEX))
        conn.commit()
    # Solo migrar y eliminar columna si next_action aún existe (evita duplicados)
    insp = inspect(engine)
    cols = [c["name"] for c in insp.get_columns("projects")]
    if "next_action" in cols:
        with engine.connect() as conn:
            conn.execute(text(MIGRATE_DATA))
            conn.execute(text(DROP_COLUMN))
            conn.commit()
        print("Tabla project_next_actions creada, datos migrados, columna projects.next_action eliminada.")
    else:
        print("Tabla project_next_actions ya existente; projects.next_action ya eliminada.")
