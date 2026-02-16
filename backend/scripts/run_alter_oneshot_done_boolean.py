"""
Corrige el tipo de la columna one_shot_tasks.done a BOOLEAN si está como integer.
Idempotente: solo altera si el tipo actual no es boolean.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text, inspect
from app.database import engine

# Convertir integer (0/1) a boolean
ALTER_DONE_BOOLEAN = """
ALTER TABLE one_shot_tasks
ALTER COLUMN done TYPE boolean USING (COALESCE(done, 0)::int != 0);
"""

# Asegurar default por si acaso
SET_DEFAULT = """
ALTER TABLE one_shot_tasks ALTER COLUMN done SET DEFAULT false;
"""


if __name__ == "__main__":
    insp = inspect(engine)
    cols = insp.get_columns("one_shot_tasks")
    done_col = next((c for c in cols if c["name"] == "done"), None)
    if not done_col:
        print("Columna one_shot_tasks.done no encontrada.")
        sys.exit(0)
    # type puede ser Boolean, Integer, etc. (objeto SQLAlchemy)
    type_name = str(done_col["type"]).upper()
    if "INT" in type_name or "SMALLINT" in type_name:
        with engine.connect() as conn:
            conn.execute(text(ALTER_DONE_BOOLEAN))
            conn.execute(text(SET_DEFAULT))
            conn.commit()
        print("Columna one_shot_tasks.done convertida a BOOLEAN.")
    else:
        print("Columna one_shot_tasks.done ya es BOOLEAN (o no requiere cambio).")
