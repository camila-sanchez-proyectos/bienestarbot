-- Agrega categoria y aplica_beca a la tabla deporte (segun la Guia de Deportes).
-- No borra datos. Se puede repetir sin problema.
USE bienestarbot;

ALTER TABLE deporte ADD COLUMN IF NOT EXISTS categoria VARCHAR(60) NULL;
ALTER TABLE deporte ADD COLUMN IF NOT EXISTS aplica_beca TINYINT(1) NOT NULL DEFAULT 0;

UPDATE deporte SET categoria = 'Femenino y masculino' WHERE nombre LIKE 'Baloncesto%' OR nombre LIKE 'Voleibol%' OR nombre LIKE 'Voley%' OR nombre LIKE 'Rugby%' OR nombre LIKE '%sala%';
UPDATE deporte SET categoria = 'Masculino' WHERE nombre LIKE 'F%tbol%' AND nombre NOT LIKE '%sala%';
UPDATE deporte SET categoria = 'Mixto' WHERE nombre LIKE 'Taekwondo%' OR nombre LIKE 'Tenis%';

UPDATE deporte SET aplica_beca = 0;
UPDATE deporte SET aplica_beca = 1
 WHERE nombre LIKE 'Ajedrez%' OR nombre LIKE 'Rugby%' OR nombre LIKE 'Taekwondo%' OR nombre LIKE 'Tenis%'
    OR (nombre LIKE 'F%tbol%' AND nombre NOT LIKE '%sala%');

SELECT nombre, categoria, aplica_beca FROM deporte ORDER BY nombre;
