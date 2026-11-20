-- Descripciones de los deportes. Solo cambia la columna descripcion. Se puede repetir.
SET NAMES utf8mb4;
USE bienestarbot;

UPDATE deporte SET descripcion = 'Desarrolla la concentración, la memoria y el pensamiento estratégico.' WHERE nombre = 'Ajedrez';
UPDATE deporte SET descripcion = 'Fomenta la agilidad, la coordinación y el trabajo en equipo.' WHERE nombre = 'Baloncesto';
UPDATE deporte SET descripcion = 'Promueve la cultura y las tradiciones mediante la música y el baile.' WHERE nombre = 'Danza folclórica';
UPDATE deporte SET descripcion = 'Fortalece las habilidades deportivas, la condición física y el trabajo en equipo.' WHERE nombre = 'Fútbol';
UPDATE deporte SET descripcion = 'Desarrolla habilidades técnicas y tácticas. Semillero y selección de la Universidad.' WHERE nombre = 'Fútbol sala';
UPDATE deporte SET descripcion = 'Promueve la resistencia, la disciplina y el trabajo en equipo. Semillero y selección de la Universidad.' WHERE nombre = 'Rugby';
UPDATE deporte SET descripcion = 'Fortalece la disciplina, el autocontrol y la condición física.' WHERE nombre = 'Taekwondo';
UPDATE deporte SET descripcion = 'Desarrolla los reflejos, la agilidad y la concentración.' WHERE nombre = 'Tenis de mesa';
UPDATE deporte SET descripcion = 'Fomenta la coordinación, la comunicación y el trabajo en equipo.' WHERE nombre = 'Voleibol';

SELECT nombre, descripcion FROM deporte ORDER BY nombre;
