-- Columnas nuevas para guardar el formulario de inscripción.
-- Ejecutar una sola vez (se puede repetir sin problema: IF NOT EXISTS).
-- No borra datos.
USE bienestarbot;

ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS telefono VARCHAR(20) NULL;
ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS rama VARCHAR(20) NULL;
ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS nivel VARCHAR(20) NULL;
ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS interes_seleccion TINYINT(1) NOT NULL DEFAULT 0;
ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS interes_beca TINYINT(1) NOT NULL DEFAULT 0;
ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS observaciones VARCHAR(300) NULL;
ALTER TABLE inscripcion ADD COLUMN IF NOT EXISTS acepta_datos TINYINT(1) NOT NULL DEFAULT 0;
