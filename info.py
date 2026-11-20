"""Información fija del área de Deportes.

Fuente: Guía de deportes, actividad física y recreación, Bienestar Universitario,
Universidad Simón Bolívar, sede Cúcuta. El panel y el chat leen estos mismos textos.
"""

# (nombre, modalidad, imagen de static/img)
DISCIPLINAS = [
    ("Ajedrez", "Categoría única", "chess"),
    ("Danza folclórica", "Mixto", "danzas"),
    ("Baloncesto", "Femenino y masculino", "basket"),
    ("Fútbol sala", "Femenino y masculino", "futsal"),
    ("Fútbol", "Masculino", "soccer"),
    ("Rugby", "Masculino y femenino", "football"),
    ("Taekwondo", "Mixto", "taekwondo"),
    ("Tenis de mesa", "Mixto", "pingpong"),
    ("Voleibol", "Femenino y masculino", "volley"),
]
IMAGENES = {nombre: imagen for nombre, _, imagen in DISCIPLINAS}

CONTACTO = {
    "area": "Área de Deportes · Bienestar Universitario · Universidad Simón Bolívar, sede Cúcuta",
    "coordinador": "Eden Francoise Barrera Duarte",
    "correo": "coordinaciondeportes@unisimonbolivar.edu.co",
    "pbx": "(607) 582 7070, extensión 112",
    "pagina": "https://www.unisimon.edu.co/cucuta/servicios/bienestaruniversitario",
}

SERVICIOS = [
    {
        "id": "gimnasio",
        "titulo": "Gimnasio universitario",
        "resumen": "Gratis para estudiantes",
        "lineas": [
            "El uso del gimnasio es gratuito para los estudiantes.",
            "Primero debes hacerte una valoración médica en el área de Salud de la Universidad.",
            "Después se acuerdan los días en que quieres asistir. La programación depende de la disponibilidad, porque a veces grupos numerosos ocupan el gimnasio.",
            "El gimnasio cuenta con un entrenador. Si eres principiante o necesitas orientación, puedes pedirle ayuda mientras asistes.",
            "Horario: 9:00 a. m. a 1:00 p. m. en la mañana y 3:00 p. m. a 7:00 p. m. en la tarde.",
            "La valoración médica y la coordinación de los días deben hacerse antes de empezar a usarlo con regularidad.",
        ],
    },
    {
        "id": "piscina",
        "titulo": "Piscina y Aqua Gym",
        "resumen": "Reserva con una semana de anticipación",
        "lineas": [
            "Reserva de la piscina: el grupo debe ir a la oficina y hablar con el encargado de Deportes.",
            "La solicitud se hace con una semana de anticipación, indicando el día que se quiere usar la piscina.",
            "Cada grupo debe ser de mínimo 8 y máximo 15 personas.",
            "El encargado revisa la disponibilidad y define el día. La fecha no queda confirmada hasta que la agende.",
            "Aqua Gym: sesiones grupales para grupos de 8 a 15 personas. Requiere inscripción previa y valoración en el área de Salud Integral. Ubicación: Sede 4 – Bloque G.",
            "Lleva ropa adecuada para actividad acuática y, las mujeres, gorro de natación.",
            "Contacto de Aqua Gym: 317 647 0845 / (607) 582 7070, extensión 112.",
        ],
    },
    {
        "id": "becas",
        "titulo": "Becas deportivas",
        "resumen": "Solo para algunas disciplinas",
        "lineas": [
            "Aplican únicamente para Ajedrez, Fútbol, Rugby (masculino y femenino), Taekwondo y Tenis de mesa. No se extienden automáticamente a las demás disciplinas.",
            "La aplicación, los porcentajes y los requisitos se revisan según el Reglamento de Becas (Acuerdo 40 de 2024) y la evaluación institucional.",
            "Como referencia del reglamento: hasta 30 % para medallistas de oro en competencias reconocidas y hasta 15 % para deportistas de alto rendimiento o representantes culturales destacados. Un deportista de alto rendimiento de nuevo ingreso puede tener una beca del 50 % en el primer semestre.",
            "Requisitos generales: promedio PPP mínimo de 3,70 en 2026 y 2027; no tener asignaturas reprobadas ni habilitaciones; matrícula completa; estar inscrito en actividades de Bienestar al inicio del periodo; asistencia y participación mínima del 80 %.",
            "La asignación final depende también de la evaluación, los logros deportivos y la disponibilidad presupuestal.",
            "En el primer mes de cada semestre se hace una evaluación de habilidades con el entrenador asignado. Contacta al entrenador de tu disciplina y confirma el horario de la prueba.",
        ],
    },
    {
        "id": "ascun",
        "titulo": "Juegos ASCUN",
        "resumen": "Solo para quienes representan a la Universidad",
        "lineas": [
            "La participación se gestiona desde la Universidad y se comunica a cada disciplina deportiva.",
            "Bienestar Universitario realiza la inscripción de los deportistas y ASCUN la revisa y la aprueba.",
            "La Universidad suele publicar información en sus redes sociales cuando sus equipos participan.",
            "Es un proceso para integrantes que representan a la Universidad. No es una convocatoria abierta a personas externas.",
        ],
    },
    {
        "id": "semilleros",
        "titulo": "Semilleros y selecciones",
        "resumen": "Para empezar o para representar a la Universidad",
        "lineas": [
            "Todos los equipos tienen semilleros: espacios de aprendizaje y formación para quienes están empezando o quieren desarrollar sus habilidades.",
            "Dentro de cada disciplina también están los deportistas seleccionados, que representan oficialmente a la Universidad en competencias.",
            "Participar en un semillero no significa formar parte de la selección. La representación corresponde a quienes son seleccionados.",
        ],
    },
    {
        "id": "contacto",
        "titulo": "Contacto del área de Deportes",
        "resumen": "Coordinación y teléfonos",
        "lineas": [
            CONTACTO["area"],
            "Coordinador: " + CONTACTO["coordinador"],
            "Correo: " + CONTACTO["correo"],
            "PBX: " + CONTACTO["pbx"],
            "Página: " + CONTACTO["pagina"],
        ],
    },
]
SERVICIOS_POR_ID = {s["id"]: s for s in SERVICIOS}
