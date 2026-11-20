-- Bienestarbot: crea la base de datos y todas las tablas y vistas que usa la aplicacion.
-- Se puede ejecutar varias veces: no borra nada (usa IF NOT EXISTS).
-- Despues cargue los datos con sql/datos_reales.sql o sql/horarios_guia.sql.
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS bienestarbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bienestarbot;

CREATE TABLE IF NOT EXISTS usuario (
  id_usuario           INT AUTO_INCREMENT PRIMARY KEY,
  nombre               VARCHAR(100) NOT NULL,
  correo_institucional VARCHAR(150) NOT NULL,
  contrasena_hash      VARCHAR(255) NOT NULL,
  rol                  VARCHAR(20)  NOT NULL DEFAULT 'estudiante',
  carrera              VARCHAR(100) NULL,
  semestre             INT NULL,
  fecha_registro       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_usuario_correo (correo_institucional)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS instructor (
  id_instructor INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL,
  especialidad  VARCHAR(100) NULL,
  contacto      VARCHAR(50)  NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS instalacion (
  id_instalacion INT AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(100) NOT NULL,
  informacion    VARCHAR(500) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS deporte (
  id_deporte    INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL,
  descripcion   VARCHAR(255) NULL,
  categoria     VARCHAR(60)  NULL,
  aplica_beca   TINYINT(1)   NOT NULL DEFAULT 0,
  cupo_maximo   INT          NOT NULL DEFAULT 30,
  id_instructor INT NULL,
  CONSTRAINT fk_deporte_instructor FOREIGN KEY (id_instructor) REFERENCES instructor (id_instructor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS horario (
  id_horario     INT AUTO_INCREMENT PRIMARY KEY,
  id_deporte     INT NOT NULL,
  id_instalacion INT NOT NULL,
  dia_semana     VARCHAR(10) NOT NULL,
  hora_inicio    TIME NOT NULL,
  hora_fin       TIME NOT NULL,
  CONSTRAINT fk_horario_deporte    FOREIGN KEY (id_deporte)     REFERENCES deporte (id_deporte),
  CONSTRAINT fk_horario_instalacion FOREIGN KEY (id_instalacion) REFERENCES instalacion (id_instalacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS evento (
  id_evento    INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  descripcion  VARCHAR(500) NULL,
  fecha_evento DATETIME NOT NULL,
  lugar        VARCHAR(150) NULL,
  capacidad    INT NOT NULL DEFAULT 50
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Una inscripcion es a un deporte o a un evento (uno de los dos queda en NULL).
-- estado: inscrito, asistio, no_asistio, cancelado
CREATE TABLE IF NOT EXISTS inscripcion (
  id_inscripcion    INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario        INT NOT NULL,
  id_deporte        INT NULL,
  id_evento         INT NULL,
  estado            VARCHAR(20) NOT NULL DEFAULT 'inscrito',
  fecha_inscripcion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  telefono          VARCHAR(20)  NULL,
  rama              VARCHAR(20)  NULL,
  nivel             VARCHAR(20)  NULL,
  interes_seleccion TINYINT(1)   NOT NULL DEFAULT 0,
  interes_beca      TINYINT(1)   NOT NULL DEFAULT 0,
  observaciones     VARCHAR(300) NULL,
  acepta_datos      TINYINT(1)   NOT NULL DEFAULT 0,
  UNIQUE KEY uq_insc_usuario_deporte (id_usuario, id_deporte),
  UNIQUE KEY uq_insc_usuario_evento  (id_usuario, id_evento),
  CONSTRAINT fk_insc_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario),
  CONSTRAINT fk_insc_deporte FOREIGN KEY (id_deporte) REFERENCES deporte (id_deporte),
  CONSTRAINT fk_insc_evento  FOREIGN KEY (id_evento)  REFERENCES evento (id_evento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS novedad (
  id_novedad        INT AUTO_INCREMENT PRIMARY KEY,
  titulo            VARCHAR(100) NOT NULL,
  contenido         VARCHAR(500) NOT NULL,
  fecha_publicacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS comentario (
  id_comentario    INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario       INT NOT NULL,
  texto            VARCHAR(1000) NOT NULL,
  fecha_comentario DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_comentario_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Vistas de cupos (las cancelaciones liberan el cupo)
CREATE OR REPLACE VIEW vista_cupos_deporte AS
SELECT d.id_deporte, d.nombre, d.cupo_maximo,
       d.cupo_maximo - COUNT(i.id_inscripcion) AS cupos_disponibles
FROM deporte d
LEFT JOIN inscripcion i ON i.id_deporte = d.id_deporte AND i.estado <> 'cancelado'
GROUP BY d.id_deporte, d.nombre, d.cupo_maximo;

CREATE OR REPLACE VIEW vista_cupos_evento AS
SELECT e.id_evento, e.nombre, e.capacidad,
       e.capacidad - COUNT(i.id_inscripcion) AS cupos_disponibles
FROM evento e
LEFT JOIN inscripcion i ON i.id_evento = e.id_evento AND i.estado <> 'cancelado'
GROUP BY e.id_evento, e.nombre, e.capacidad;
