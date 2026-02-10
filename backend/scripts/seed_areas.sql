-- Inserta áreas de ejemplo en la tabla areas.
-- Asigna las áreas al usuario con email 'test@lifehub.local'.
-- Ejecutar una vez contra la BD (ej: psql o desde Docker).

INSERT INTO areas (user_id, name, description, created_at, updated_at)
SELECT u.id, v.name, NULL, NOW(), NOW()
FROM users u
CROSS JOIN (VALUES
  ('Vida social'),
  ('Creatividad y ocio'),
  ('Finanzas personales'),
  ('Vida doméstica'),
  ('Cuerpo y salud'),
  ('Compromisos externos')
) AS v(name)
WHERE u.email = 'test@lifehub.local'
  AND NOT EXISTS (
    SELECT 1 FROM areas a
    WHERE a.user_id = u.id AND a.name = v.name
  );
