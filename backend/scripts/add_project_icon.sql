-- Añade la columna icon a projects (para emoji junto al título).
-- Ejecutar solo si la tabla projects ya existía antes de esta funcionalidad.

ALTER TABLE projects ADD COLUMN IF NOT EXISTS icon VARCHAR(20) NULL;
