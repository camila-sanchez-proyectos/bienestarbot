"""Explicaciones de cada deporte para el chat (qué es, cómo se juega, qué necesitas)."""
import re

# clave -> nombre, palabras que lo identifican (sin tildes), y las tres explicaciones.
DEPORTES = {
    "ajedrez": {
        "nombre": "Ajedrez",
        "palabras": ["ajedrez"],
        "que_es": "El ajedrez es un juego de estrategia para dos personas que se juega sobre un tablero de 64 casillas. Cada jugador empieza con 16 piezas: un rey, una dama, dos torres, dos alfiles, dos caballos y ocho peones. Es un deporte mental: no se corre, se piensa.",
        "como_se": "Se juega por turnos y empiezan las piezas blancas. Cada pieza se mueve de forma distinta. El objetivo es dar jaque mate: atacar al rey rival de modo que no pueda escapar. Si un jugador no tiene ningún movimiento legal y su rey no está atacado, la partida queda en tablas (empate). Si nunca lo has jugado, lo primero es aprender cómo se mueve cada pieza.",
        "necesitas": "Solo un tablero, las piezas y, en partidas con tiempo, un reloj. Entrena la concentración, la memoria, la paciencia y la planeación. No necesitas experiencia previa.",
    },
    "baloncesto": {
        "nombre": "Baloncesto",
        "palabras": ["baloncesto", "basquet", "basquetbol", "basket"],
        "que_es": "El baloncesto es un deporte de equipo. Juegan dos equipos de cinco jugadores y el objetivo es meter el balón en el aro del equipo contrario, que está a unos 3 metros de altura.",
        "como_se": "Se avanza botando el balón con una mano (driblando) o pasándolo a un compañero; no se puede caminar con él en las manos. Un tiro libre vale 1 punto, una canasta normal 2 y un tiro desde detrás de la línea de tres puntos vale 3. El partido se juega en cuatro cuartos y gana el equipo con más puntos.",
        "necesitas": "Un balón de baloncesto, tenis y ropa cómoda. Mejora la coordinación, la resistencia, el salto y el trabajo en equipo. Puedes empezar sin experiencia.",
    },
    "futbol sala": {
        "nombre": "Fútbol sala",
        "palabras": ["futbol sala", "futsal", "microfutbol", "futbol de salon"],
        "que_es": "El fútbol sala es una versión del fútbol que se juega en una cancha más pequeña y de piso duro. Cada equipo tiene cinco jugadores: cuatro de campo y un portero. El balón es más pequeño y pesado, y rebota poco.",
        "como_se": "Se juega con los pies (solo el portero usa las manos dentro de su área) y gana el equipo que meta más goles. El partido dura dos tiempos de 20 minutos. Es muy rápido: hay muchos pases cortos, y las faltas acumuladas tienen consecuencias.",
        "necesitas": "Tenis de piso plano o de fútbol sala y ropa cómoda; se recomiendan canilleras. Mejora la agilidad, el control del balón y la resistencia. No necesitas experiencia previa.",
    },
    "futbol": {
        "nombre": "Fútbol",
        "palabras": ["futbol", "football", "soccer"],
        "que_es": "El fútbol es el deporte de equipo más practicado del mundo. Juegan dos equipos de 11 jugadores y el objetivo es meter el balón en el arco contrario.",
        "como_se": "Se juega con los pies, la cabeza y el cuerpo; solo el portero puede usar las manos dentro de su área. Gana el equipo que anote más goles en 90 minutos (dos tiempos de 45). Entre las reglas básicas están el fuera de juego, las faltas y las tarjetas: amarilla de advertencia y roja de expulsión.",
        "necesitas": "Guayos o tenis, canilleras y ropa deportiva. Mejora la resistencia, la coordinación y el trabajo en equipo. Si nunca lo has practicado, puedes empezar en el semillero.",
    },
    "rugby": {
        "nombre": "Rugby",
        "palabras": ["rugby", "rugbi"],
        "que_es": "El rugby es un deporte de equipo y de contacto que se juega con un balón ovalado. El objetivo es llevar el balón detrás de la línea de marca del rival, lo que se llama ensayo.",
        "como_se": "Se avanza corriendo con el balón en las manos, y los pases solo pueden ser hacia atrás o hacia los lados, nunca hacia adelante. Se puede detener al rival que lleva el balón con un placaje, por debajo de los hombros. Un ensayo vale 5 puntos y la conversión posterior suma 2 más; también se anotan puntos con patadas. Es un deporte de mucho respeto: se juega duro pero limpio.",
        "necesitas": "Ropa resistente, protector bucal y calzado deportivo; el entrenador te indica el resto. Desarrolla la fuerza, la resistencia, la disciplina y el trabajo en equipo. Se aprende desde cero y se empieza con la técnica antes del contacto.",
    },
    "taekwondo": {
        "nombre": "Taekwondo",
        "palabras": ["taekwondo", "tae kwon do", "tkd"],
        "que_es": "El taekwondo es un arte marcial de origen coreano que se destaca por el uso de las patadas. Es deporte olímpico y también ayuda a la defensa personal y al autocontrol.",
        "como_se": "Se practica con un uniforme llamado dobok y un cinturón cuyo color indica tu nivel; se empieza con el cinturón blanco. Se entrena con ejercicios de técnica y formas (poomsae), y en el combate se ganan puntos con golpes válidos al tronco y a la cabeza, siempre con protecciones.",
        "necesitas": "Ropa cómoda para empezar; el entrenador te dice cuándo conseguir el dobok y las protecciones. Mejora la flexibilidad, el equilibrio, la disciplina y la confianza. No necesitas experiencia previa.",
    },
    "tenis de mesa": {
        "nombre": "Tenis de mesa",
        "palabras": ["tenis de mesa", "ping pong", "pingpong", "ping-pong"],
        "que_es": "El tenis de mesa, o ping pong, es un deporte de raqueta que se juega sobre una mesa dividida por una red, con una pelota muy liviana. Se puede jugar de a uno contra uno o en dobles.",
        "como_se": "Cada jugador golpea la pelota con su paleta para que bote en el lado del rival. Se gana el punto cuando el otro no logra devolverla bien. Los sets se juegan a 11 puntos con diferencia de 2, y el partido es al mejor de cinco o siete sets. El saque cambia cada dos puntos.",
        "necesitas": "Una paleta (en la práctica se puede prestar al comienzo) y ropa cómoda. Mejora los reflejos, la coordinación entre ojos y manos y la concentración, con muy poco impacto en el cuerpo.",
    },
    "voleibol": {
        "nombre": "Voleibol",
        "palabras": ["voleibol", "voley", "volley", "volleyball", "balonvolea"],
        "que_es": "El voleibol es un deporte de equipo en el que dos equipos de seis jugadores se enfrentan en una cancha dividida por una red alta.",
        "como_se": "El objetivo es que el balón toque el suelo del lado contrario, y evitar que caiga en el tuyo. Cada equipo puede tocarlo hasta tres veces antes de pasarlo por encima de la red (recibir, armar y rematar). Los sets son a 25 puntos con diferencia de 2 y el partido es al mejor de cinco sets. Los jugadores rotan de posición.",
        "necesitas": "Tenis, ropa cómoda y, si quieres, rodilleras. Mejora la coordinación, el salto y el trabajo en equipo. Puedes empezar sin experiencia.",
    },
}

# Palabras que indican que la persona quiere una explicación y no una acción.
_PREGUNTA = ("que es", "que son", "como se juega", "como se practica", "como funciona",
             "reglas", "explic", "en que consiste", "de que trata", "no se que",
             "no conozco", "no se como se", "que implementos", "que necesito",
             "que se necesita", "beneficio", "para que sirve", "que hace",
             "nunca he jugado", "nunca he practicado", "principiante", "cuentame",
             "que significa", "como es el", "como es la")
_ACCION = ("inscrib", "cancel", "horario", "cupo", "entrenador", "instructor",
           "profesor", "beca", "cuando", "donde")


def deporte_en(t):
    """Clave del deporte que menciona el texto (ya normalizado), o None.
    'americano' devuelve 'americano' porque ese deporte no se ofrece."""
    if re.search(r"\bfutbol americano\b", t):
        return "americano"
    # Primero los nombres más largos ("futbol sala" antes que "futbol").
    candidatos = []
    for clave, d in DEPORTES.items():
        for p in d["palabras"]:
            if re.search(r"\b" + re.escape(p) + r"\b", t):
                candidatos.append((len(p), clave))
    return max(candidatos)[1] if candidatos else None


def es_pregunta(t):
    if any(a in t for a in _ACCION):
        return False
    return any(p in t for p in _PREGUNTA)
