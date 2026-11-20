"""Simón, el chatbot de Deportes de BienestarBot: funciona por reglas y botones.

Recibe lo que el estudiante toca o escribe, consulta MySQL y devuelve
mensajes de texto y botones de respuesta rápida.
"""
import unicodedata
from datetime import datetime, timedelta

from mysql.connector import IntegrityError

from db import get_connection
from info import SERVICIOS, SERVICIOS_POR_ID
import conocimiento

# Tabla, columna de id y columna de cupo de cada tipo de actividad.
# Estos nombres son fijos (nunca vienen del usuario).
# Datos del formulario de inscripción que se guardan (nombres fijos de columnas).
CAMPOS_FORMULARIO = ("telefono", "rama", "nivel", "interes_seleccion",
                     "interes_beca", "observaciones", "acepta_datos")

TIPOS = {
    "deporte": ("deporte", "id_deporte", "cupo_maximo"),
    "evento": ("evento", "id_evento", "capacidad"),
}
ESTADOS = {"inscrito": "inscrito", "asistio": "asistió", "no_asistio": "no asistió"}


# ---------- utilidades ----------

def normalizar(texto):
    """Minúsculas y sin tildes, para reconocer palabras clave."""
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def btn(texto, **payload):
    return {"texto": texto, "payload": payload}


def respuesta(mensaje, botones=None, esperar=None, ok=False):
    return {"mensajes": [mensaje], "botones": botones or [], "esperar": esperar, "ok": ok}


def menu():
    return [
        btn("Ver deportes", accion="deportes"),
        btn("Inscribirme", accion="inscribirme"),
        btn("Mis inscripciones", accion="mis"),
        btn("Cancelar inscripción", accion="cancelar"),
        btn("Horarios e instalaciones", accion="horarios"),
        btn("Instructores", accion="instructores"),
        btn("Eventos", accion="eventos"),
        btn("Novedades", accion="novedades"),
        btn("Servicios y becas", accion="servicios"),
        btn("Comentarios", accion="comentario"),
    ]


def hora(valor):
    """MySQL entrega TIME como timedelta: lo mostramos como HH:MM."""
    if isinstance(valor, timedelta):
        minutos = int(valor.total_seconds() // 60)
        return f"{minutos // 60:02d}:{minutos % 60:02d}"
    return str(valor)[:5]


def fecha(valor):
    return valor.strftime("%d/%m/%Y %H:%M")


DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def lista_dias(dias):
    """['Lunes','Miércoles','Viernes'] -> 'Lunes, miércoles y viernes'."""
    if len(dias) == 7:
        return "Toda la semana"
    nombres = [d.lower() for d in dias]
    texto = nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]
    return texto[0].upper() + texto[1:]


def agrupar_horarios(filas):
    """Junta los días que comparten hora y lugar en una sola línea."""
    grupos = {}
    for h in filas:
        clave = (hora(h["hora_inicio"]), hora(h["hora_fin"]), h["lugar"])
        grupos.setdefault(clave, []).append(h["dia_semana"])
    return [
        {"dias": lista_dias(sorted(set(dias), key=DIAS.index)),
         "inicio": ini, "fin": fin, "lugar": lugar}
        for (ini, fin, lugar), dias in grupos.items()
    ]


def entero(d, clave):
    try:
        return int(d.get(clave))
    except (TypeError, ValueError):
        return None


def texto_cupos(libres, total):
    if libres <= 0:
        return "Cupo lleno"
    return f"Cupos disponibles: {libres} de {total}"


def solo_estudiante(u):
    if u["rol"] != "estudiante":
        return respuesta(
            "Las inscripciones son para estudiantes. Como administrador, "
            "puedes consultar la información desde este chat.",
            [btn("Menú", accion="menu")],
        )
    return None


# ---------- interpretar lo que escribe el estudiante ----------

REGLAS = [
    (("mis inscripciones", "mis deportes", "en que estoy"), "mis"),
    (("cancel", "anular", "darme de baja", "retirar"), "cancelar"),
    (("inscrib", "unirme", "apuntar", "quiero entrar"), "inscribirme"),
    (("horario", "instalacion", "cancha", "coliseo"), "horarios"),
    (("instructor", "entrenador", "profesor", "profe", "coach"), "instructores"),
    (("evento", "torneo", "campeonato"), "eventos"),
    (("gimnasio", "gym", "pesas"), "servicio:gimnasio"),
    (("piscina", "aqua", "natacion"), "servicio:piscina"),
    (("beca",), "servicio:becas"),
    (("ascun",), "servicio:ascun"),
    (("semillero", "seleccion"), "servicio:semilleros"),
    (("contacto", "coordinador", "telefono", "correo de deportes"), "servicio:contacto"),
    (("servicio",), "servicios"),
    (("novedad", "noticia", "anuncio"), "novedades"),
    (("comentario", "sugerencia", "queja", "opinion", "reclamo"), "comentario"),
    (("explic", "conocer un deporte", "no se que deporte", "no se cual deporte"), "explicar_menu"),
    (("deporte", "disciplina", "ofrecen", "ofrece"), "deportes"),
    (("hola", "buenas", "menu", "ayuda", "inicio", "gracias"), "menu"),
]


def interpretar(cur, texto):
    t = normalizar(texto)
    if not t:
        return {"accion": "menu"}

    # ¿Pregunta qué es o cómo se juega un deporte? Se le explica.
    if conocimiento.es_pregunta(t):
        clave = conocimiento.deporte_en(t)
        if clave:
            return {"accion": "explicar", "clave": clave}

    # ¿Menciona un deporte? Se prefiere el nombre más largo ("futbol americano").
    cur.execute("SELECT id_deporte, nombre FROM deporte")
    mencionado = None
    for f in cur.fetchall():
        n = normalizar(f["nombre"])
        if n in t and (mencionado is None or len(n) > mencionado[0]):
            mencionado = (len(n), f["id_deporte"])
    if mencionado:
        if "inscrib" in t:
            return {"accion": "confirmar_inscripcion", "tipo": "deporte", "id": mencionado[1]}
        if "cancel" not in t:
            return {"accion": "deporte", "id": mencionado[1]}

    for palabras, accion in REGLAS:
        if any(p in t for p in palabras):
            if accion.startswith("servicio:"):
                return {"accion": "servicio", "id": accion.split(":", 1)[1]}
            return {"accion": accion}
    return {"accion": "no_entendi"}


# ---------- acciones ----------

def accion_menu(con, cur, u, d):
    nombre = u["nombre"].split()[0]
    return respuesta(
        f"Hola, {nombre}. Soy Simón, el asistente de Deportes de Bienestar "
        "Universitario. ¿Qué quieres hacer? Usa los botones o escríbeme, por ejemplo "
        "«horarios» o «quiero inscribirme».",
        menu(),
    )


def accion_no_entendi(con, cur, u, d):
    return respuesta(
        "No puedo ayudarte con esa información. Si deseas conocer más sobre los deportes, "
        "pregúntame aquí; estaré para ayudarte.",
        [btn("Explícame un deporte", accion="explicar_menu")] + menu(),
    )


def accion_explicar_menu(con, cur, u, d):
    botones = [btn(x["nombre"], accion="explicar", clave=k) for k, x in conocimiento.DEPORTES.items()]
    botones.append(btn("Menú", accion="menu"))
    return respuesta("Con gusto te explico cualquier deporte. ¿Cuál quieres conocer?", botones)


def accion_explicar(con, cur, u, d):
    clave = d.get("clave")
    if clave == "americano":
        return respuesta(
            "El fútbol americano no hace parte de la oferta de Deportes. El más parecido es "
            "el rugby. ¿Quieres que te explique alguno de los deportes que sí tenemos?",
            [btn("Explícame un deporte", accion="explicar_menu"), btn("Menú", accion="menu")],
        )
    x = conocimiento.DEPORTES.get(clave)
    if not x:
        return accion_explicar_menu(con, cur, u, d)
    botones = []
    cur.execute("SELECT id_deporte, nombre FROM deporte")
    for f in cur.fetchall():
        if normalizar(f["nombre"]) == normalizar(x["nombre"]):
            botones.append(btn(f"Ver horarios y cupos de {f['nombre']}", accion="deporte", id=f["id_deporte"]))
            break
    botones += [btn("Explícame otro deporte", accion="explicar_menu"), btn("Menú", accion="menu")]
    return {
        "mensajes": [
            f"{x['nombre']}: {x['que_es']}",
            f"Cómo se juega: {x['como_se']}",
            f"Qué necesitas: {x['necesitas']} ¿Te animas? Puedes inscribirte cuando quieras.",
        ],
        "botones": botones, "esperar": None, "ok": False,
    }


def accion_deportes(con, cur, u, d):
    cur.execute(
        "SELECT id_deporte, nombre, cupos_disponibles "
        "FROM vista_cupos_deporte ORDER BY nombre"
    )
    filas = cur.fetchall()
    if not filas:
        return respuesta("Todavía no hay deportes publicados.", menu())
    lineas = ["Estos son los deportes disponibles. Toca uno para ver el detalle:"]
    for f in filas:
        libres = f["cupos_disponibles"]
        estado = "cupo lleno" if libres <= 0 else f"{libres} {'cupo libre' if libres == 1 else 'cupos libres'}"
        lineas.append(f"• {f['nombre']}: {estado}")
    botones = [btn(f["nombre"], accion="deporte", id=f["id_deporte"]) for f in filas]
    botones.append(btn("Menú", accion="menu"))
    return respuesta("\n".join(lineas), botones)


def accion_deporte(con, cur, u, d):
    idn = entero(d, "id")
    cur.execute(
        "SELECT dep.nombre, dep.descripcion, dep.categoria, dep.aplica_beca, "
        "       ins.nombre AS instructor, ins.especialidad, ins.contacto, "
        "       v.cupo_maximo, v.cupos_disponibles "
        "FROM deporte dep "
        "JOIN vista_cupos_deporte v ON v.id_deporte = dep.id_deporte "
        "LEFT JOIN instructor ins ON ins.id_instructor = dep.id_instructor "
        "WHERE dep.id_deporte = %s",
        (idn,),
    )
    f = cur.fetchone()
    if not f:
        return respuesta("No encontré ese deporte.", [btn("Ver deportes", accion="deportes")])

    cur.execute(
        "SELECT h.dia_semana, h.hora_inicio, h.hora_fin, i.nombre AS lugar "
        "FROM horario h JOIN instalacion i ON i.id_instalacion = h.id_instalacion "
        "WHERE h.id_deporte = %s "
        "ORDER BY FIELD(h.dia_semana,'Lunes','Martes','Miércoles','Jueves',"
        "'Viernes','Sábado','Domingo'), h.hora_inicio",
        (idn,),
    )
    horarios = cur.fetchall()

    lineas = [f["nombre"] + (f" ({f['categoria']})" if f["categoria"] else "")]
    if f["descripcion"]:
        lineas.append(f["descripcion"])
    if f["instructor"]:
        contacto = f" · {f['contacto']}" if f["contacto"] else ""
        lineas.append(f"Instructor: {f['instructor']}{contacto}")
    else:
        lineas.append("Instructor: por confirmar")
    if horarios:
        lineas.append("Horarios:")
        for h in agrupar_horarios(horarios):
            lineas.append(f"• {h['dias']} {h['inicio']} a {h['fin']}, {h['lugar']}")
    else:
        lineas.append("Horarios: por confirmar con el área de Deportes")
    if f["aplica_beca"]:
        lineas.append("Esta disciplina aplica a beca deportiva.")
    lineas.append(texto_cupos(f["cupos_disponibles"], f["cupo_maximo"]))

    botones = []
    if f["cupos_disponibles"] > 0 and u["rol"] == "estudiante":
        botones.append(btn(f"Inscribirme en {f['nombre']}", accion="confirmar_inscripcion", tipo="deporte", id=idn))
    botones += [btn("Ver deportes", accion="deportes"), btn("Menú", accion="menu")]
    return respuesta("\n".join(lineas), botones)


def accion_inscribirme(con, cur, u, d):
    bloqueo = solo_estudiante(u)
    if bloqueo:
        return bloqueo
    cur.execute("SELECT id_deporte, nombre FROM deporte ORDER BY nombre")
    deportes = cur.fetchall()
    cur.execute(
        "SELECT id_evento, nombre FROM evento WHERE fecha_evento >= NOW() ORDER BY fecha_evento"
    )
    eventos = cur.fetchall()
    if not deportes and not eventos:
        return respuesta("Todavía no hay deportes ni eventos para inscribirse.", menu())
    botones = [btn(f["nombre"], accion="confirmar_inscripcion", tipo="deporte", id=f["id_deporte"]) for f in deportes]
    botones += [btn(f"Evento: {f['nombre']}", accion="confirmar_inscripcion", tipo="evento", id=f["id_evento"]) for f in eventos]
    botones.append(btn("Menú", accion="menu"))
    return respuesta("¿En qué deporte o evento quieres inscribirte?", botones)


def deporte_activo(cur, id_usuario):
    """Deporte en el que el estudiante ya esta inscrito (o None). Solo se permite uno."""
    cur.execute(
        "SELECT d.id_deporte, d.nombre FROM inscripcion i "
        "JOIN deporte d ON d.id_deporte = i.id_deporte "
        "WHERE i.id_usuario = %s AND i.id_deporte IS NOT NULL AND i.estado <> 'cancelado' "
        "LIMIT 1",
        (id_usuario,),
    )
    return cur.fetchone()


def respuesta_un_deporte(activo, idn):
    if activo["id_deporte"] == idn:
        return respuesta(
            f"Ya estás inscrito en {activo['nombre']}.",
            [btn("Mis inscripciones", accion="mis"), btn("Menú", accion="menu")],
        )
    return respuesta(
        f"Ya estás inscrito en {activo['nombre']}. Solo puedes practicar un deporte a la vez. "
        "Si quieres cambiar, primero cancela esa inscripción.",
        [btn("Cancelar una inscripción", accion="cancelar"),
         btn("Mis inscripciones", accion="mis"), btn("Menú", accion="menu")],
    )


def accion_confirmar_inscripcion(con, cur, u, d):
    bloqueo = solo_estudiante(u)
    if bloqueo:
        return bloqueo
    tipo, idn = d.get("tipo"), entero(d, "id")
    if tipo not in TIPOS or idn is None:
        return accion_no_entendi(con, cur, u, d)
    tabla, col, _ = TIPOS[tipo]
    cur.execute(f"SELECT nombre FROM {tabla} WHERE {col} = %s", (idn,))
    f = cur.fetchone()
    if not f:
        return respuesta("No encontré esa actividad.", menu())
    if tipo == "deporte":
        activo = deporte_activo(cur, u["id"])
        if activo:
            return respuesta_un_deporte(activo, idn)
    return respuesta(
        f"Para inscribirte en {f['nombre']} debes llenar el formulario de inscripción.",
        [
            btn("Llenar formulario", url=f"/inscripcion/{tipo}/{idn}"),
            btn("No, volver", accion="menu"),
        ],
    )


def accion_inscribir(con, cur, u, d):
    """RF9 y RF10: inscribe validando cupo y que no esté repetida."""
    bloqueo = solo_estudiante(u)
    if bloqueo:
        return bloqueo
    tipo, idn = d.get("tipo"), entero(d, "id")
    if tipo not in TIPOS or idn is None:
        return accion_no_entendi(con, cur, u, d)
    tabla, col, col_cupo = TIPOS[tipo]
    otros = "Ver otros deportes" if tipo == "deporte" else "Ver eventos"
    otros_accion = "deportes" if tipo == "deporte" else "eventos"

    formulario = d.get("form")
    if not isinstance(formulario, dict):
        return respuesta(
            "Para inscribirte primero llena el formulario de inscripción.",
            [btn("Llenar formulario", url=f"/inscripcion/{tipo}/{idn}"),
             btn("Menú", accion="menu")],
        )
    extra = {k: formulario[k] for k in CAMPOS_FORMULARIO if k in formulario}

    con.commit()  # cierra cualquier lectura anterior antes de bloquear la fila
    try:
        # Se bloquea la fila de la actividad para que dos estudiantes no
        # tomen el último cupo al mismo tiempo.
        cur.execute(f"SELECT * FROM {tabla} WHERE {col} = %s FOR UPDATE", (idn,))
        act = cur.fetchone()
        if not act:
            con.rollback()
            return respuesta("No encontré esa actividad.", menu())
        if tipo == "evento" and act["fecha_evento"] < datetime.now():
            con.rollback()
            return respuesta(
                f"El evento {act['nombre']} ya pasó.",
                [btn(otros, accion=otros_accion), btn("Menú", accion="menu")],
            )

        cur.execute(
            f"SELECT id_inscripcion, estado FROM inscripcion "
            f"WHERE id_usuario = %s AND {col} = %s",
            (u["id"], idn),
        )
        previa = cur.fetchone()
        if previa and previa["estado"] != "cancelado":
            con.rollback()
            return respuesta(
                f"Ya estás inscrito en {act['nombre']}.",
                [btn("Mis inscripciones", accion="mis"), btn("Menú", accion="menu")],
            )

        if tipo == "deporte":
            activo = deporte_activo(cur, u["id"])
            if activo and activo["id_deporte"] != idn:
                con.rollback()
                return respuesta_un_deporte(activo, idn)

        cur.execute(
            f"SELECT COUNT(*) AS n FROM inscripcion WHERE {col} = %s AND estado <> 'cancelado'",
            (idn,),
        )
        ocupados = cur.fetchone()["n"]
        if ocupados >= act[col_cupo]:
            con.rollback()
            return respuesta(
                f"Lo siento, el cupo de {act['nombre']} está lleno. "
                "Puedes elegir otra opción o intentarlo más tarde.",
                [btn(otros, accion=otros_accion), btn("Menú", accion="menu")],
            )

        if previa:  # se había cancelado: se reactiva la misma inscripción
            sets = "".join(f", {k} = %s" for k in extra)
            cur.execute(
                "UPDATE inscripcion SET estado = 'inscrito', fecha_inscripcion = NOW()"
                f"{sets} WHERE id_inscripcion = %s",
                (*extra.values(), previa["id_inscripcion"]),
            )
        else:
            columnas = ["id_usuario", col, *extra]
            cur.execute(
                f"INSERT INTO inscripcion ({', '.join(columnas)}) "
                f"VALUES ({', '.join(['%s'] * len(columnas))})",
                (u["id"], idn, *extra.values()),
            )
        con.commit()
    except IntegrityError:
        con.rollback()
        return respuesta(
            f"Ya estabas inscrito en {act['nombre']}.",
            [btn("Mis inscripciones", accion="mis"), btn("Menú", accion="menu")],
        )

    libres = act[col_cupo] - ocupados - 1
    quedan = "Queda 1 cupo" if libres == 1 else f"Quedan {libres} cupos"
    return respuesta(
        f"Listo, quedaste inscrito en {act['nombre']}. {quedan}. "
        "Puedes cancelar cuando quieras desde tu panel o desde este chat.",
        [btn("Mis inscripciones", accion="mis"), btn("Menú", accion="menu")],
        ok=True,
    )


def inscripciones_de(cur, id_usuario, solo_inscritas):
    filtro = "i.estado = 'inscrito'" if solo_inscritas else "i.estado <> 'cancelado'"
    cur.execute(
        "SELECT i.id_inscripcion, i.estado, i.id_deporte, i.id_evento, "
        "       COALESCE(d.nombre, e.nombre) AS nombre "
        "FROM inscripcion i "
        "LEFT JOIN deporte d ON d.id_deporte = i.id_deporte "
        "LEFT JOIN evento e ON e.id_evento = i.id_evento "
        f"WHERE i.id_usuario = %s AND {filtro} "
        "ORDER BY i.fecha_inscripcion DESC",
        (id_usuario,),
    )
    return cur.fetchall()


def accion_mis(con, cur, u, d):
    filas = inscripciones_de(cur, u["id"], solo_inscritas=False)
    if not filas:
        return respuesta(
            "Todavía no tienes inscripciones.",
            [btn("Inscribirme", accion="inscribirme"), btn("Menú", accion="menu")],
        )
    lineas = ["Tus inscripciones:"]
    for f in filas:
        tipo = "Evento" if f["id_evento"] else "Deporte"
        lineas.append(f"• {tipo}: {f['nombre']} ({ESTADOS.get(f['estado'], f['estado'])})")
    return respuesta(
        "\n".join(lineas),
        [btn("Cancelar inscripción", accion="cancelar"), btn("Menú", accion="menu")],
    )


def accion_cancelar(con, cur, u, d):
    filas = inscripciones_de(cur, u["id"], solo_inscritas=True)
    if not filas:
        return respuesta(
            "No tienes inscripciones activas para cancelar.",
            [btn("Inscribirme", accion="inscribirme"), btn("Menú", accion="menu")],
        )
    botones = [btn(f"Cancelar {f['nombre']}", accion="confirmar_cancelacion", id=f["id_inscripcion"]) for f in filas]
    botones.append(btn("Menú", accion="menu"))
    return respuesta("¿Cuál inscripción quieres cancelar?", botones)


def accion_confirmar_cancelacion(con, cur, u, d):
    idn = entero(d, "id")
    cur.execute(
        "SELECT COALESCE(dep.nombre, ev.nombre) AS nombre "
        "FROM inscripcion i "
        "LEFT JOIN deporte dep ON dep.id_deporte = i.id_deporte "
        "LEFT JOIN evento ev ON ev.id_evento = i.id_evento "
        "WHERE i.id_inscripcion = %s AND i.id_usuario = %s AND i.estado = 'inscrito'",
        (idn, u["id"]),
    )
    f = cur.fetchone()
    if not f:
        return respuesta("No encontré esa inscripción activa.", menu())
    return respuesta(
        f"¿Seguro que quieres cancelar tu inscripción en {f['nombre']}? El cupo quedará libre.",
        [
            btn("Sí, cancelar", accion="cancelar_ok", id=idn),
            btn("No, volver", accion="menu"),
        ],
    )


def accion_cancelar_ok(con, cur, u, d):
    """RF11: cancela solo inscripciones del propio estudiante."""
    idn = entero(d, "id")
    cur.execute(
        "UPDATE inscripcion SET estado = 'cancelado' "
        "WHERE id_inscripcion = %s AND id_usuario = %s AND estado = 'inscrito'",
        (idn, u["id"]),
    )
    cambiadas = cur.rowcount
    con.commit()
    if not cambiadas:
        return respuesta("No encontré esa inscripción activa.", menu())
    return respuesta(
        "Listo, cancelé tu inscripción. El cupo quedó libre para otro estudiante.",
        [btn("Inscribirme", accion="inscribirme"), btn("Menú", accion="menu")],
        ok=True,
    )


def accion_horarios(con, cur, u, d):
    cur.execute(
        "SELECT dep.nombre AS deporte, h.dia_semana, h.hora_inicio, h.hora_fin, "
        "       i.nombre AS lugar "
        "FROM horario h "
        "JOIN deporte dep ON dep.id_deporte = h.id_deporte "
        "JOIN instalacion i ON i.id_instalacion = h.id_instalacion "
        "ORDER BY dep.nombre, FIELD(h.dia_semana,'Lunes','Martes','Miércoles',"
        "'Jueves','Viernes','Sábado','Domingo'), h.hora_inicio"
    )
    filas = cur.fetchall()
    if not filas:
        return respuesta(
            "Todavía no hay horarios publicados. Bienestar los irá agregando.",
            [btn("Menú", accion="menu")],
        )
    por_deporte = {}
    for f in filas:
        por_deporte.setdefault(f["deporte"], []).append(f)
    lineas = ["Horarios e instalaciones:"]
    for deporte, grupo in por_deporte.items():
        lineas.append("")
        lineas.append(deporte)
        for h in agrupar_horarios(grupo):
            lineas.append(f"• {h['dias']} {h['inicio']} a {h['fin']}, {h['lugar']}")
    return respuesta("\n".join(lineas), [btn("Ver deportes", accion="deportes"), btn("Menú", accion="menu")])


def accion_instructores(con, cur, u, d):
    cur.execute(
        "SELECT i.nombre, i.especialidad, i.contacto, "
        "       GROUP_CONCAT(dep.nombre ORDER BY dep.nombre SEPARATOR ', ') AS deportes "
        "FROM instructor i LEFT JOIN deporte dep ON dep.id_instructor = i.id_instructor "
        "GROUP BY i.id_instructor, i.nombre, i.especialidad, i.contacto "
        "ORDER BY i.nombre"
    )
    filas = cur.fetchall()
    if not filas:
        return respuesta("Todavía no hay instructores registrados.", [btn("Menú", accion="menu")])
    lineas = ["Instructores de Deportes:"]
    for f in filas:
        lineas.append("")
        lineas.append(f["nombre"])
        if f["especialidad"]:
            lineas.append(f"Especialidad: {f['especialidad']}")
        if f["deportes"]:
            lineas.append(f"Deportes: {f['deportes']}")
        if f["contacto"]:
            lineas.append(f"Contacto: {f['contacto']}")
    return respuesta("\n".join(lineas), [btn("Ver deportes", accion="deportes"), btn("Menú", accion="menu")])


def accion_eventos(con, cur, u, d):
    cur.execute(
        "SELECT e.id_evento, e.nombre, e.descripcion, e.fecha_evento, e.lugar, "
        "       v.cupos_disponibles "
        "FROM evento e JOIN vista_cupos_evento v ON v.id_evento = e.id_evento "
        "WHERE e.fecha_evento >= NOW() ORDER BY e.fecha_evento"
    )
    filas = cur.fetchall()
    if not filas:
        return respuesta("No hay eventos próximos por ahora.", [btn("Menú", accion="menu")])
    lineas, botones = ["Próximos eventos:"], []
    for f in filas:
        lineas.append("")
        lineas.append(f["nombre"])
        if f["descripcion"]:
            lineas.append(f["descripcion"])
        lineas.append(f"Fecha: {fecha(f['fecha_evento'])}. Lugar: {f['lugar']}")
        lineas.append("Cupo lleno" if f["cupos_disponibles"] <= 0 else f"Cupos disponibles: {f['cupos_disponibles']}")
        if f["cupos_disponibles"] > 0 and u["rol"] == "estudiante":
            botones.append(btn(f"Inscribirme en {f['nombre']}", accion="confirmar_inscripcion", tipo="evento", id=f["id_evento"]))
    botones.append(btn("Menú", accion="menu"))
    return respuesta("\n".join(lineas), botones)


def accion_novedades(con, cur, u, d):
    cur.execute(
        "SELECT titulo, contenido, fecha_publicacion FROM novedad "
        "ORDER BY fecha_publicacion DESC LIMIT 5"
    )
    filas = cur.fetchall()
    if not filas:
        return respuesta("No hay novedades publicadas por ahora.", [btn("Menú", accion="menu")])
    lineas = ["Últimas novedades:"]
    for f in filas:
        lineas.append("")
        lineas.append(f"{f['titulo']} ({f['fecha_publicacion'].strftime('%d/%m/%Y')})")
        lineas.append(f["contenido"])
    return respuesta("\n".join(lineas), [btn("Menú", accion="menu")])


def accion_servicios(con, cur, u, d):
    botones = [btn(sv["titulo"], accion="servicio", id=sv["id"]) for sv in SERVICIOS]
    botones.append(btn("Menú", accion="menu"))
    return respuesta("¿Sobre qué servicio del área quieres información?", botones)


def accion_servicio(con, cur, u, d):
    sv = SERVICIOS_POR_ID.get(d.get("id"))
    if not sv:
        return accion_servicios(con, cur, u, d)
    texto = sv["titulo"] + "\n" + "\n".join("• " + linea for linea in sv["lineas"])
    return respuesta(texto, [btn("Otros servicios", accion="servicios"), btn("Menú", accion="menu")])


def accion_comentario(con, cur, u, d):
    return respuesta(
        "Escribe tu comentario o sugerencia para Bienestar Universitario y envíalo.",
        [btn("Volver al menú", accion="menu")],
        esperar="comentario",
    )


def accion_guardar_comentario(con, cur, u, d):
    """RF12: guarda el comentario del estudiante."""
    texto = (d.get("texto") or "").strip()
    if len(texto) < 3:
        return respuesta(
            "El comentario es muy corto. Escríbelo de nuevo.",
            [btn("Volver al menú", accion="menu")],
            esperar="comentario",
        )
    cur.execute(
        "INSERT INTO comentario (id_usuario, texto) VALUES (%s, %s)",
        (u["id"], texto[:1000]),
    )
    con.commit()
    return respuesta("Gracias, recibimos tu comentario.", [btn("Menú", accion="menu")])


ACCIONES = {
    "menu": accion_menu,
    "no_entendi": accion_no_entendi,
    "explicar": accion_explicar,
    "explicar_menu": accion_explicar_menu,
    "deportes": accion_deportes,
    "deporte": accion_deporte,
    "inscribirme": accion_inscribirme,
    "confirmar_inscripcion": accion_confirmar_inscripcion,
    "inscribir": accion_inscribir,
    "mis": accion_mis,
    "cancelar": accion_cancelar,
    "confirmar_cancelacion": accion_confirmar_cancelacion,
    "cancelar_ok": accion_cancelar_ok,
    "horarios": accion_horarios,
    "instructores": accion_instructores,
    "eventos": accion_eventos,
    "novedades": accion_novedades,
    "servicios": accion_servicios,
    "servicio": accion_servicio,
    "comentario": accion_comentario,
    "guardar_comentario": accion_guardar_comentario,
}


def procesar(usuario, datos):
    """Punto de entrada: `usuario` es {id, nombre, rol}; `datos` viene del navegador."""
    con = get_connection()
    try:
        cur = con.cursor(dictionary=True)
        accion = datos.get("accion")
        if accion not in ACCIONES:
            texto = str(datos.get("texto") or "")[:500]
            datos = interpretar(cur, texto)
            accion = datos["accion"]
        return ACCIONES[accion](con, cur, usuario, datos)
    finally:
        con.close()
