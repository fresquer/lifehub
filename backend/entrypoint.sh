#!/bin/sh
set -e

# Migraciones: se ejecutan en cada arranque (son idempotentes con IF NOT EXISTS).
echo "Ejecutando migraciones..."
python /app/scripts/run_add_area_color.py
python /app/scripts/run_add_project_icon.py
echo "Migraciones listas."

exec "$@"
