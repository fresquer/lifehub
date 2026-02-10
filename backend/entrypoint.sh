#!/bin/sh
set -e

# Migración única: deja el esquema al día (tablas + columnas). Idempotente.
echo "Ejecutando migraciones..."
python /app/scripts/run_migrate_all.py
echo "Migraciones listas."

exec "$@"
