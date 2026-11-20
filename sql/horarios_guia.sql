-- Carga entrenadores, lugares y horarios segun la Guia de Deportes.
-- Agrega Rugby y Futbol sala. No borra inscripciones. Se puede repetir.
SET NAMES utf8mb4;
USE bienestarbot;

-- 1) Lugares
INSERT INTO instalacion (nombre)
SELECT x.n FROM (
  SELECT 'Estadio de atletismo de Atalaya' AS n UNION ALL
  SELECT 'Cancha Los Copetes' UNION ALL
  SELECT 'Salón de ajedrez, sede 2' UNION ALL
  SELECT 'Zona común, sede 4') x
WHERE NOT EXISTS (SELECT 1 FROM instalacion i WHERE i.nombre = x.n);

-- 2) Entrenadores
INSERT INTO instructor (nombre, especialidad, contacto)
SELECT x.n, x.e, x.c FROM (
  SELECT 'Juan Miguel Moreno' AS n, 'Rugby' AS e, '321 213 3277' AS c UNION ALL
  SELECT 'Eduardo Arias', 'Voleibol y fútbol sala', '316 527 9094' UNION ALL
  SELECT 'Diego Sánchez', 'Ajedrez', '311 406 7190' UNION ALL
  SELECT 'Angie Peñaranda', 'Taekwondo', '305 753 7510' UNION ALL
  SELECT 'Keyla Quevedo', 'Tenis de mesa', '312 652 5805' UNION ALL
  SELECT 'César Ibarra', 'Fútbol', '315 585 7270') x
WHERE NOT EXISTS (SELECT 1 FROM instructor i WHERE i.nombre = x.n);

-- 3) Deportes nuevos (cupo_maximo 30 por defecto: cambialo si es otro)
INSERT INTO deporte (nombre, descripcion, cupo_maximo)
SELECT 'Rugby', 'Rugby masculino y femenino. Semillero y selección de la Universidad.', 30
WHERE NOT EXISTS (SELECT 1 FROM deporte WHERE nombre = 'Rugby');
INSERT INTO deporte (nombre, descripcion, cupo_maximo)
SELECT 'Fútbol sala', 'Fútbol sala femenino y masculino. Semillero y selección de la Universidad.', 30
WHERE NOT EXISTS (SELECT 1 FROM deporte WHERE nombre = 'Fútbol sala');

-- 4) Categoria, beca y entrenador de cada deporte
UPDATE deporte SET categoria = NULL, aplica_beca = 0;
UPDATE deporte SET categoria='Femenino y masculino' WHERE nombre IN ('Baloncesto','Fútbol sala','Voleibol');
UPDATE deporte SET categoria='Masculino y femenino' WHERE nombre = 'Rugby';
UPDATE deporte SET categoria='Masculino' WHERE nombre = 'Fútbol';
UPDATE deporte SET categoria='Mixto' WHERE nombre IN ('Taekwondo','Tenis de mesa');
UPDATE deporte SET aplica_beca=1 WHERE nombre IN ('Ajedrez','Fútbol','Rugby','Taekwondo','Tenis de mesa');

UPDATE deporte SET id_instructor=(SELECT id_instructor FROM instructor WHERE nombre='Juan Miguel Moreno' LIMIT 1) WHERE nombre='Rugby';
UPDATE deporte SET id_instructor=(SELECT id_instructor FROM instructor WHERE nombre='Eduardo Arias' LIMIT 1) WHERE nombre IN ('Voleibol','Fútbol sala');
UPDATE deporte SET id_instructor=(SELECT id_instructor FROM instructor WHERE nombre='Diego Sánchez' LIMIT 1) WHERE nombre='Ajedrez';
UPDATE deporte SET id_instructor=(SELECT id_instructor FROM instructor WHERE nombre='Angie Peñaranda' LIMIT 1) WHERE nombre='Taekwondo';
UPDATE deporte SET id_instructor=(SELECT id_instructor FROM instructor WHERE nombre='Keyla Quevedo' LIMIT 1) WHERE nombre='Tenis de mesa';
UPDATE deporte SET id_instructor=(SELECT id_instructor FROM instructor WHERE nombre='César Ibarra' LIMIT 1) WHERE nombre='Fútbol';
UPDATE deporte SET id_instructor=NULL WHERE nombre='Baloncesto';

-- 5) Horarios (se reemplazan solo los de estos 7 deportes)
DELETE FROM horario WHERE id_deporte IN
  (SELECT id_deporte FROM deporte WHERE nombre IN ('Rugby','Voleibol','Fútbol sala','Ajedrez','Taekwondo','Tenis de mesa','Fútbol'));

DROP TEMPORARY TABLE IF EXISTS tmp_h;
CREATE TEMPORARY TABLE tmp_h (dep VARCHAR(80), lugar VARCHAR(100), dia VARCHAR(12), ini TIME, fin TIME);
INSERT INTO tmp_h VALUES
 ('Rugby','Estadio de atletismo de Atalaya','Lunes','15:00','17:00'),
 ('Rugby','Estadio de atletismo de Atalaya','Miércoles','15:00','17:00'),
 ('Rugby','Estadio de atletismo de Atalaya','Viernes','15:00','17:00'),
 ('Voleibol','Cancha Los Copetes','Lunes','12:00','16:00'),
 ('Voleibol','Cancha Los Copetes','Miércoles','12:00','16:00'),
 ('Voleibol','Cancha Los Copetes','Viernes','12:00','16:00'),
 ('Fútbol sala','Cancha Los Copetes','Martes','12:00','14:00'),
 ('Fútbol sala','Cancha Los Copetes','Jueves','12:00','14:00'),
 ('Fútbol sala','Cancha Los Copetes','Sábado','08:00','12:00'),
 ('Ajedrez','Salón de ajedrez, sede 2','Lunes','08:00','10:00'),
 ('Ajedrez','Salón de ajedrez, sede 2','Jueves','08:00','10:00'),
 ('Ajedrez','Salón de ajedrez, sede 2','Viernes','08:00','10:00'),
 ('Taekwondo','Zona común, sede 4','Lunes','12:30','15:00'),
 ('Taekwondo','Zona común, sede 4','Martes','12:30','15:00'),
 ('Taekwondo','Zona común, sede 4','Miércoles','12:30','15:00'),
 ('Taekwondo','Zona común, sede 4','Jueves','12:30','15:00'),
 ('Taekwondo','Zona común, sede 4','Viernes','12:30','15:00'),
 ('Taekwondo','Zona común, sede 4','Sábado','12:30','15:00'),
 ('Taekwondo','Zona común, sede 4','Domingo','12:30','15:00'),
 ('Tenis de mesa','Zona común, sede 4','Lunes','14:00','16:00'),
 ('Tenis de mesa','Zona común, sede 4','Miércoles','14:00','16:00'),
 ('Tenis de mesa','Zona común, sede 4','Jueves','14:00','16:00'),
 ('Fútbol','Cancha Los Copetes','Lunes','12:00','14:00'),
 ('Fútbol','Cancha Los Copetes','Miércoles','12:00','14:00'),
 ('Fútbol','Cancha Los Copetes','Jueves','12:00','14:00');

INSERT INTO horario (id_deporte, id_instalacion, dia_semana, hora_inicio, hora_fin)
SELECT d.id_deporte, (SELECT MIN(i.id_instalacion) FROM instalacion i WHERE i.nombre = t.lugar), t.dia, t.ini, t.fin
FROM tmp_h t JOIN deporte d ON d.nombre = t.dep;
DROP TEMPORARY TABLE tmp_h;

-- 6) Resultado
SELECT d.nombre, d.categoria, d.aplica_beca, i.nombre AS entrenador,
       (SELECT COUNT(*) FROM horario h WHERE h.id_deporte = d.id_deporte) AS horarios
FROM deporte d LEFT JOIN instructor i ON i.id_instructor = d.id_instructor ORDER BY d.nombre;
