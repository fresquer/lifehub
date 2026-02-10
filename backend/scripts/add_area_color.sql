-- Añade la columna color a areas (hex #rrggbb para la paleta).
-- Ejecutar solo si la tabla areas ya existía antes de esta funcionalidad.

ALTER TABLE areas ADD COLUMN IF NOT EXISTS color VARCHAR(7) NULL;
