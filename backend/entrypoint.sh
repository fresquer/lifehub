#!/bin/sh
set -e

# Migración única: deja el esquema al día (tablas + columnas, p. ej. projects.next_action). Idempotente.
# Se ejecuta en cada arranque del contenedor (docker compose up, despliegue).
echo "Ejecutando migraciones..."
python /app/scripts/run_migrate_all.py
python /app/scripts/run_add_oneshot_area_id.py
python /app/scripts/run_alter_oneshot_done_boolean.py
python /app/scripts/run_add_project_next_actions.py
echo "Migraciones listas."

exec "$@"
