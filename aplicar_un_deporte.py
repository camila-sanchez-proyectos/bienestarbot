"""Regla: un estudiante solo puede estar inscrito en UN deporte a la vez.
Ejecutar desde la carpeta del proyecto:  python aplicar_un_deporte.py
Se puede repetir sin problema. Guarda copias .bak."""
import pathlib, shutil

def parchar(archivo, cambios):
    f = pathlib.Path(archivo)
    t = f.read_text(encoding="utf-8")
    if "deporte_activo" in t:
        print(f"{archivo}: ya estaba aplicado")
        return
    for viejo, nuevo in cambios:
        if t.count(viejo) != 1:
            raise SystemExit(f"{archivo}: no encontre el punto de insercion:\n{viejo[:80]}...\n"
                             "No se cambio nada en este archivo. Avisame.")
        t = t.replace(viejo, nuevo)
    shutil.copy(f, str(f) + ".bak")
    f.write_text(t, encoding="utf-8")
    print(f"{archivo}: actualizado")

AYUDA = '''def deporte_activo(cur, id_usuario):
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


def accion_confirmar_inscripcion(con, cur, u, d):'''

parchar("chatbot.py", [
    ("def accion_confirmar_inscripcion(con, cur, u, d):", AYUDA),
    ('''        return respuesta("No encontré esa actividad.", menu())
    return respuesta(
        f"Para inscribirte en {f['nombre']} debes llenar el formulario de inscripción.",''',
     '''        return respuesta("No encontré esa actividad.", menu())
    if tipo == "deporte":
        activo = deporte_activo(cur, u["id"])
        if activo:
            return respuesta_un_deporte(activo, idn)
    return respuesta(
        f"Para inscribirte en {f['nombre']} debes llenar el formulario de inscripción.",'''),
    ('''        cur.execute(
            f"SELECT COUNT(*) AS n FROM inscripcion WHERE {col} = %s AND estado <> 'cancelado'",''',
     '''        if tipo == "deporte":
            activo = deporte_activo(cur, u["id"])
            if activo and activo["id_deporte"] != idn:
                con.rollback()
                return respuesta_un_deporte(activo, idn)

        cur.execute(
            f"SELECT COUNT(*) AS n FROM inscripcion WHERE {col} = %s AND estado <> 'cancelado'",'''),
])

parchar("app.py", [
    ("from chatbot import procesar, ESTADOS", "from chatbot import procesar, ESTADOS, deporte_activo"),
    ('''    act = cargar_actividad(tipo, idn)
    if not act:
        abort(404)
''',
     '''    act = cargar_actividad(tipo, idn)
    if not act:
        abort(404)
    if tipo == "deporte":
        con = get_connection()
        try:
            activo = deporte_activo(con.cursor(dictionary=True), int(current_user.id))
        finally:
            con.close()
        if activo and activo["id_deporte"] != idn:
            flash(f"Ya estás inscrito en {activo['nombre']}. Solo puedes practicar un deporte "
                  "a la vez; cancela esa inscripción si quieres cambiar.", "error")
            return redirect(url_for("panel", _anchor="mensajes"))
'''),
])
