"""Datos que se muestran en el panel del estudiante (todo sale de MySQL)."""
from chatbot import agrupar_horarios, fecha, inscripciones_de
from db import get_connection
from info import CONTACTO, IMAGENES, SERVICIOS


def cargar_panel(id_usuario):
    con = get_connection()
    try:
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT d.id_deporte, d.nombre, d.descripcion, d.categoria, d.aplica_beca, "
            "       d.cupo_maximo, "
            "       v.cupos_disponibles, i.nombre AS instructor, "
            "       i.especialidad, i.contacto "
            "FROM deporte d "
            "JOIN vista_cupos_deporte v ON v.id_deporte = d.id_deporte "
            "LEFT JOIN instructor i ON i.id_instructor = d.id_instructor "
            "ORDER BY d.nombre"
        )
        deportes = cur.fetchall()

        cur.execute(
            "SELECT h.id_deporte, h.dia_semana, h.hora_inicio, h.hora_fin, "
            "       i.nombre AS lugar "
            "FROM horario h JOIN instalacion i ON i.id_instalacion = h.id_instalacion "
            "ORDER BY FIELD(h.dia_semana,'Lunes','Martes','Miércoles','Jueves',"
            "'Viernes','Sábado','Domingo'), h.hora_inicio"
        )
        horarios = cur.fetchall()

        cur.execute(
            "SELECT e.id_evento, e.nombre, e.descripcion, e.fecha_evento, "
            "       e.lugar, e.capacidad, v.cupos_disponibles "
            "FROM evento e JOIN vista_cupos_evento v ON v.id_evento = e.id_evento "
            "WHERE e.fecha_evento >= NOW() ORDER BY e.fecha_evento"
        )
        eventos = cur.fetchall()

        cur.execute(
            "SELECT titulo, contenido, fecha_publicacion FROM novedad "
            "ORDER BY fecha_publicacion DESC LIMIT 3"
        )
        novedades = cur.fetchall()

        cur.execute("SELECT nombre, informacion FROM instalacion ORDER BY nombre")
        instalaciones = cur.fetchall()

        mias = inscripciones_de(cur, id_usuario, solo_inscritas=False)
    finally:
        con.close()

    crudos = {}
    for h in horarios:
        crudos.setdefault(h["id_deporte"], []).append(h)
    por_deporte = {i: agrupar_horarios(filas) for i, filas in crudos.items()}
    mi_deporte = {m["id_deporte"]: m for m in mias if m["id_deporte"]}
    mi_evento = {m["id_evento"]: m for m in mias if m["id_evento"]}

    for d in deportes:
        d["horarios"] = por_deporte.get(d["id_deporte"], [])
        d["imagen"] = IMAGENES.get(d["nombre"])
        d["mi"] = mi_deporte.get(d["id_deporte"])
        ocupados = d["cupo_maximo"] - d["cupos_disponibles"]
        d["ocupacion"] = round(100 * ocupados / d["cupo_maximo"]) if d["cupo_maximo"] else 0
    for e in eventos:
        e["fecha_txt"] = fecha(e["fecha_evento"])
        e["mi"] = mi_evento.get(e["id_evento"])
    for n in novedades:
        n["fecha_txt"] = n["fecha_publicacion"].strftime("%d/%m/%Y")

    return {
        "deportes": deportes,
        "eventos": eventos,
        "novedades": novedades,
        "instalaciones": instalaciones,
        "mis_inscripciones": mias,
        "servicios": SERVICIOS,
        "contacto": CONTACTO,
    }


def ramas_de(categoria):
    """Ramas entre las que se puede elegir según la categoría del deporte."""
    c = (categoria or "").lower()
    if "femenino" in c and "masculino" in c:
        return ["Femenino", "Masculino"]
    if "masculino" in c:
        return ["Masculino"]
    if "femenino" in c:
        return ["Femenino"]
    return []


def cargar_actividad(tipo, idn):
    """Datos de un deporte o evento para mostrar en el formulario de inscripción."""
    con = get_connection()
    try:
        cur = con.cursor(dictionary=True)
        if tipo == "deporte":
            cur.execute(
                "SELECT d.id_deporte, d.nombre, d.descripcion, d.categoria, d.aplica_beca, "
                "       d.cupo_maximo, v.cupos_disponibles, i.nombre AS instructor, "
                "       i.especialidad, i.contacto "
                "FROM deporte d "
                "JOIN vista_cupos_deporte v ON v.id_deporte = d.id_deporte "
                "LEFT JOIN instructor i ON i.id_instructor = d.id_instructor "
                "WHERE d.id_deporte = %s", (idn,))
            act = cur.fetchone()
            if not act:
                return None
            cur.execute(
                "SELECT h.id_deporte, h.dia_semana, h.hora_inicio, h.hora_fin, "
                "       i.nombre AS lugar "
                "FROM horario h JOIN instalacion i ON i.id_instalacion = h.id_instalacion "
                "WHERE h.id_deporte = %s "
                "ORDER BY FIELD(h.dia_semana,'Lunes','Martes','Miércoles','Jueves',"
                "'Viernes','Sábado','Domingo'), h.hora_inicio", (idn,))
            act["horarios"] = agrupar_horarios(cur.fetchall())
            act["ramas"] = ramas_de(act["categoria"])
        else:
            cur.execute(
                "SELECT e.id_evento, e.nombre, e.descripcion, e.fecha_evento, "
                "       e.lugar, e.capacidad, v.cupos_disponibles "
                "FROM evento e JOIN vista_cupos_evento v ON v.id_evento = e.id_evento "
                "WHERE e.id_evento = %s", (idn,))
            act = cur.fetchone()
            if not act:
                return None
            act["fecha_txt"] = fecha(act["fecha_evento"])
    finally:
        con.close()
    return act
