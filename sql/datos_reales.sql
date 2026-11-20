ALTER TABLE deporte ADD COLUMN IF NOT EXISTS categoria VARCHAR(60) NULL;
ALTER TABLE deporte ADD COLUMN IF NOT EXISTS aplica_beca TINYINT(1) NOT NULL DEFAULT 0;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE horario;
TRUNCATE TABLE inscripcion;
TRUNCATE TABLE deporte;
TRUNCATE TABLE instructor;
TRUNCATE TABLE instalacion;
TRUNCATE TABLE evento;
TRUNCATE TABLE novedad;
SET FOREIGN_KEY_CHECKS = 1;
INSERT INTO instalacion (nombre, informacion) VALUES
('Estadio de atletismo de Atalaya', 'Rugby.'),
('Cancha Los Copetes', 'Voleibol, fútbol sala y fútbol.'),
('Salón de ajedrez, sede 2', 'Ajedrez.'),
('Zona común, sede 4', 'Taekwondo y tenis de mesa.'),
('Gimnasio universitario', 'Gratis para estudiantes. Requiere valoración médica previa. Horario: 9:00 a. m. a 1:00 p. m. y 3:00 p. m. a 7:00 p. m.'),
('Piscina', 'Se reserva con una semana de anticipación en la oficina de Deportes, para grupos de 8 a 15 personas.');
INSERT INTO instructor (nombre, especialidad, contacto) VALUES
('Juan Miguel Moreno', 'Rugby', '321 213 3277'),
('Eduardo Arias', 'Voleibol y fútbol sala', '316 527 9094'),
('Diego Sánchez', 'Ajedrez', '311 406 7190'),
('Angie Peñaranda', 'Taekwondo', '305 753 7510'),
('Keyla Quevedo', 'Tenis de mesa', '312 652 5805'),
('César Ibarra', 'Fútbol', '315 585 7270');
INSERT INTO deporte (nombre, descripcion, categoria, aplica_beca, cupo_maximo) VALUES
('Ajedrez', 'Cuenta con semillero y con selección de la Universidad.', 'Categoría única', 1, 20),
('Baloncesto', 'Aún no hay entrenador vigente. Solicita el horario y la inscripción en el área de Deportes.', 'Femenino y masculino', 0, 30),
('Fútbol sala', 'Cuenta con semillero y con selección de la Universidad.', 'Femenino y masculino', 0, 30),
('Fútbol', 'Cuenta con semillero y con selección de la Universidad.', 'Masculino', 1, 30),
('Rugby', 'Cuenta con semillero y con selección de la Universidad.', 'Masculino y femenino', 1, 30),
('Taekwondo', 'Cuenta con semillero y con selección de la Universidad.', 'Mixto', 1, 25),
('Tenis de mesa', 'Cuenta con semillero y con selección de la Universidad.', 'Mixto', 1, 20),
('Voleibol', 'Cuenta con semillero y con selección de la Universidad.', 'Femenino y masculino', 0, 30);
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Diego Sánchez') WHERE nombre = 'Ajedrez';
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Eduardo Arias') WHERE nombre = 'Fútbol sala';
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'César Ibarra') WHERE nombre = 'Fútbol';
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Juan Miguel Moreno') WHERE nombre = 'Rugby';
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Angie Peñaranda') WHERE nombre = 'Taekwondo';
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Keyla Quevedo') WHERE nombre = 'Tenis de mesa';
UPDATE deporte SET id_instructor = (SELECT id_instructor FROM instructor WHERE nombre = 'Eduardo Arias') WHERE nombre = 'Voleibol';
INSERT INTO horario (id_deporte, id_instalacion, dia_semana, hora_inicio, hora_fin) VALUES
((SELECT id_deporte FROM deporte WHERE nombre = 'Rugby'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Estadio de atletismo de Atalaya'), 'Lunes', '15:00:00', '17:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Rugby'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Estadio de atletismo de Atalaya'), 'Miércoles', '15:00:00', '17:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Rugby'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Estadio de atletismo de Atalaya'), 'Viernes', '15:00:00', '17:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Voleibol'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Lunes', '12:00:00', '16:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Voleibol'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Miércoles', '12:00:00', '16:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Voleibol'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Viernes', '12:00:00', '16:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Fútbol sala'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Martes', '12:00:00', '14:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Fútbol sala'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Jueves', '12:00:00', '14:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Fútbol sala'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Sábado', '08:00:00', '12:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Ajedrez'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Salón de ajedrez, sede 2'), 'Lunes', '08:00:00', '10:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Ajedrez'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Salón de ajedrez, sede 2'), 'Jueves', '08:00:00', '10:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Ajedrez'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Salón de ajedrez, sede 2'), 'Viernes', '08:00:00', '10:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Lunes', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Martes', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Miércoles', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Jueves', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Viernes', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Sábado', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Taekwondo'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Domingo', '12:30:00', '15:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Tenis de mesa'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Lunes', '14:00:00', '16:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Tenis de mesa'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Miércoles', '14:00:00', '16:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Tenis de mesa'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Zona común, sede 4'), 'Jueves', '14:00:00', '16:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Fútbol'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Lunes', '12:00:00', '14:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Fútbol'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Miércoles', '12:00:00', '14:00:00'),
((SELECT id_deporte FROM deporte WHERE nombre = 'Fútbol'), (SELECT id_instalacion FROM instalacion WHERE nombre = 'Cancha Los Copetes'), 'Jueves', '12:00:00', '14:00:00');
