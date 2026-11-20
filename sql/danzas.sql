-- Danza folclórica: lugar, profesora, descripción y horarios.
-- Usa el deporte "Danza folclórica" si ya existe (y arregla el duplicado "Danzas" si lo hubo).
-- No borra inscripciones. Se puede repetir.
SET NAMES utf8mb4;
USE bienestarbot;

-- 1) Si por error quedó un "Danzas" aparte
SET @viejo := (SELECT id_deporte FROM deporte WHERE nombre = 'Danzas' LIMIT 1);
SET @bueno := (SELECT id_deporte FROM deporte WHERE nombre = 'Danza folclórica' LIMIT 1);
UPDATE deporte SET nombre = 'Danza folclórica' WHERE id_deporte = @viejo AND @bueno IS NULL;
DELETE FROM horario WHERE id_deporte = @viejo AND @bueno IS NOT NULL;
DELETE FROM deporte WHERE id_deporte = @viejo AND @bueno IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM inscripcion WHERE id_deporte = @viejo);

-- 2) Lugar y profesora
INSERT INTO instalacion (nombre)
SELECT 'Bloque cultural, sede 2, tercer piso'
WHERE NOT EXISTS (SELECT 1 FROM instalacion WHERE nombre = 'Bloque cultural, sede 2, tercer piso');

INSERT INTO instructor (nombre, especialidad, contacto)
SELECT 'Astrid Ramírez', 'Danza folclórica', '302 7488028'
WHERE NOT EXISTS (SELECT 1 FROM instructor WHERE nombre = 'Astrid Ramírez');

-- 3) El deporte (si no existe se crea con cupo 25)
INSERT INTO deporte (nombre, descripcion, categoria, aplica_beca, cupo_maximo)
SELECT 'Danza folclórica', 'Promueve la cultura y las tradiciones mediante la música y el baile.', 'Mixto', 0, 25
WHERE NOT EXISTS (SELECT 1 FROM deporte WHERE nombre = 'Danza folclórica');

UPDATE deporte
SET descripcion = 'Promueve la cultura y las tradiciones mediante la música y el baile.',
    categoria = COALESCE(categoria, 'Mixto'),
    id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Astrid Ramírez' LIMIT 1)
WHERE nombre = 'Danza folclórica';

-- 4) Horarios: lunes, miércoles y jueves de 12:00 a 14:00
SET @dep := (SELECT id_deporte FROM deporte WHERE nombre = 'Danza folclórica' LIMIT 1);
SET @lug := (SELECT id_instalacion FROM instalacion WHERE nombre = 'Bloque cultural, sede 2, tercer piso' LIMIT 1);
DELETE FROM horario WHERE id_deporte = @dep;
INSERT INTO horario (id_deporte, id_instalacion, dia_semana, hora_inicio, hora_fin) VALUES
(@dep, @lug, 'Lunes',     '12:00:00', '14:00:00'),
(@dep, @lug, 'Miércoles', '12:00:00', '14:00:00'),
(@dep, @lug, 'Jueves',    '12:00:00', '14:00:00');

SELECT d.nombre, d.cupo_maximo, i.nombre AS profesora, i.contacto
FROM deporte d JOIN instructor i ON i.id_instructor = d.id_instructor WHERE d.nombre = 'Danza folclórica';
