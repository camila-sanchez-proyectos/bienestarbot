"""Panel del administrador: gestión de deportes, horarios y eventos.

Solo entra el personal de Bienestar (cualquier rol distinto de "estudiante",
la misma regla que ya usa el chatbot). Se registra en app.py como blueprint.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from mysql.connector import Error as ErrorMySQL, IntegrityError
from werkzeug.security import generate_password_hash

from db import get_connection

bp = Blueprint("admin", __name__, url_prefix="/admin")

CATEGORIAS = ["Categoría única", "Femenino y masculino", "Masculino y femenino",
              "Masculino", "Femenino", "Mixto"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DOMINIOS_PERSONAL = ("@unisimon.edu.co", "@unisimonbolivar.edu.co")
FORMATO_FECHA = "%Y-%m-%dT%H:%M"   # el que usa <input type="datetime-local">


# ---------- utilidades ----------

@contextmanager
def conexion():
    con = get_connection()
    try:
        yield con
    finally:
        con.close()


def solo_admin(vista):
    """Deja pasar solo al personal; a un estudiante lo devuelve a su panel."""
    @wraps(vista)
    @login_required
    def envoltura(*args, **kwargs):
        if current_user.rol == "estudiante":
            flash("Esa sección es solo para el personal de Bienestar.", "error")
            return redirect(url_for("panel"))
        return vista(*args, **kwargs)
    return envoltura


@bp.app_template_filter("hhmm")
def hhmm(valor):
    """MySQL entrega las horas como timedelta; se muestran como 08:00."""
    if isinstance(valor, timedelta):
        s = int(valor.total_seconds())
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}"
    return str(valor)[:5]


@bp.app_template_filter("fecha_hora")
def fecha_hora(valor):
    return valor.strftime("%d/%m/%Y, %H:%M") if valor else ""


def entero(texto, minimo, maximo):
    texto = (texto or "").strip()
    if not texto.isdigit():
        return None
    n = int(texto)
    return n if minimo <= n <= maximo else None


def ocupados(cur, columna, idn):
    cur.execute(f"SELECT COUNT(*) AS n FROM inscripcion "
                f"WHERE {columna} = %s AND estado <> 'cancelado'", (idn,))
    return cur.fetchone()["n"]


def tiene_inscripciones(cur, columna, idn):
    cur.execute(f"SELECT COUNT(*) AS n FROM inscripcion WHERE {columna} = %s", (idn,))
    return cur.fetchone()["n"] > 0


def instructores(cur):
    cur.execute("SELECT id_instructor, nombre, especialidad FROM instructor ORDER BY nombre")
    return cur.fetchall()


# ---------- resumen ----------

@bp.route("")
@solo_admin
def inicio():
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS n FROM deporte")
        n_deportes = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM evento WHERE fecha_evento >= NOW()")
        n_eventos = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM inscripcion WHERE estado = 'inscrito'")
        n_inscritos = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM comentario")
        n_comentarios = cur.fetchone()["n"]
    return render_template("admin/inicio.html", n_deportes=n_deportes,
                           n_eventos=n_eventos, n_inscritos=n_inscritos,
                           n_comentarios=n_comentarios)


# ---------- deportes ----------

@bp.route("/deportes")
@solo_admin
def deportes():
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT d.id_deporte, d.nombre, d.categoria, d.aplica_beca, d.cupo_maximo, "
            "       v.cupos_disponibles, i.nombre AS instructor "
            "FROM deporte d "
            "JOIN vista_cupos_deporte v ON v.id_deporte = d.id_deporte "
            "LEFT JOIN instructor i ON i.id_instructor = d.id_instructor "
            "ORDER BY d.nombre")
        lista = cur.fetchall()
    return render_template("admin/deportes.html", deportes=lista)


def leer_deporte(cur, f, idn=None):
    """Valida el formulario de un deporte. Devuelve (datos, mensaje_de_error)."""
    nombre = f.get("nombre", "").strip()
    if not nombre or len(nombre) > 80:
        return None, "Escribe el nombre del deporte (máximo 80 caracteres)."
    cur.execute("SELECT id_deporte FROM deporte WHERE nombre = %s AND id_deporte <> %s",
                (nombre, idn or 0))
    if cur.fetchone():
        return None, "Ya existe un deporte con ese nombre."
    categoria = f.get("categoria", "")
    if categoria not in CATEGORIAS:
        return None, "Elige la categoría de la lista."
    cupo = entero(f.get("cupo_maximo"), 1, 500)
    if cupo is None:
        return None, "El cupo debe ser un número entre 1 y 500."
    if idn and cupo < ocupados(cur, "id_deporte", idn):
        return None, "El cupo no puede ser menor que los estudiantes ya inscritos."
    id_instructor = None
    if f.get("id_instructor"):
        id_instructor = entero(f["id_instructor"], 1, 10**9)
        cur.execute("SELECT 1 FROM instructor WHERE id_instructor = %s", (id_instructor,))
        if id_instructor is None or not cur.fetchone():
            return None, "Elige un entrenador de la lista."
    return {
        "nombre": nombre,
        "descripcion": f.get("descripcion", "").strip()[:255] or None,
        "categoria": categoria,
        "aplica_beca": 1 if f.get("aplica_beca") else 0,
        "cupo_maximo": cupo,
        "id_instructor": id_instructor,
    }, None


@bp.route("/deportes/nuevo", methods=["GET", "POST"])
@solo_admin
def deporte_nuevo():
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        if request.method == "POST":
            datos, error = leer_deporte(cur, request.form)
            if error:
                flash(error, "error")
            else:
                cur.execute(
                    "INSERT INTO deporte (nombre, descripcion, categoria, aplica_beca, "
                    "cupo_maximo, id_instructor) VALUES (%s, %s, %s, %s, %s, %s)",
                    (datos["nombre"], datos["descripcion"], datos["categoria"],
                     datos["aplica_beca"], datos["cupo_maximo"], datos["id_instructor"]))
                con.commit()
                flash(f"Listo, se creó el deporte {datos['nombre']}. "
                      "Ahora agrégale sus horarios.", "ok")
                return redirect(url_for("admin.deporte_editar", idn=cur.lastrowid))
        lista = instructores(cur)
    return render_template("admin/deporte_form.html", deporte=None, horarios=[],
                           instalaciones=[], instructores=lista,
                           categorias=CATEGORIAS, dias=DIAS)


@bp.route("/deportes/<int:idn>", methods=["GET", "POST"])
@solo_admin
def deporte_editar(idn):
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM deporte WHERE id_deporte = %s", (idn,))
        deporte = cur.fetchone()
        if not deporte:
            abort(404)
        if request.method == "POST":
            datos, error = leer_deporte(cur, request.form, idn)
            if error:
                flash(error, "error")
            else:
                cur.execute(
                    "UPDATE deporte SET nombre = %s, descripcion = %s, categoria = %s, "
                    "aplica_beca = %s, cupo_maximo = %s, id_instructor = %s "
                    "WHERE id_deporte = %s",
                    (datos["nombre"], datos["descripcion"], datos["categoria"],
                     datos["aplica_beca"], datos["cupo_maximo"], datos["id_instructor"], idn))
                con.commit()
                flash("Listo, se guardaron los cambios del deporte.", "ok")
                return redirect(url_for("admin.deporte_editar", idn=idn))
        cur.execute(
            "SELECT h.dia_semana, h.hora_inicio, h.hora_fin, h.id_instalacion, "
            "       i.nombre AS lugar "
            "FROM horario h JOIN instalacion i ON i.id_instalacion = h.id_instalacion "
            "WHERE h.id_deporte = %s "
            "ORDER BY FIELD(h.dia_semana,'Lunes','Martes','Miércoles','Jueves',"
            "'Viernes','Sábado','Domingo'), h.hora_inicio", (idn,))
        horarios = cur.fetchall()
        cur.execute("SELECT id_instalacion, nombre FROM instalacion ORDER BY nombre")
        instalaciones = cur.fetchall()
        lista = instructores(cur)
        n_ocupados = ocupados(cur, "id_deporte", idn)
    return render_template("admin/deporte_form.html", deporte=deporte, horarios=horarios,
                           instalaciones=instalaciones, instructores=lista,
                           categorias=CATEGORIAS, dias=DIAS, n_ocupados=n_ocupados)


@bp.route("/deportes/<int:idn>/eliminar", methods=["POST"])
@solo_admin
def deporte_eliminar(idn):
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT nombre FROM deporte WHERE id_deporte = %s", (idn,))
        fila = cur.fetchone()
        if not fila:
            abort(404)
        if tiene_inscripciones(cur, "id_deporte", idn):
            flash(f"No se puede eliminar {fila['nombre']}: ya tiene inscripciones "
                  "registradas. Así no se pierde el historial de los estudiantes.", "error")
            return redirect(url_for("admin.deporte_editar", idn=idn))
        try:
            cur.execute("DELETE FROM horario WHERE id_deporte = %s", (idn,))
            cur.execute("DELETE FROM deporte WHERE id_deporte = %s", (idn,))
            con.commit()
        except IntegrityError:
            con.rollback()
            flash(f"No se pudo eliminar {fila['nombre']} porque otros datos dependen de él.", "error")
            return redirect(url_for("admin.deporte_editar", idn=idn))
    flash(f"Se eliminó el deporte {fila['nombre']}.", "ok")
    return redirect(url_for("admin.deportes"))


# ---------- horarios de un deporte ----------

def _hora(texto):
    try:
        return datetime.strptime((texto or "").strip()[:5], "%H:%M").strftime("%H:%M")
    except ValueError:
        return None


@bp.route("/deportes/<int:idn>/horarios", methods=["POST"])
@solo_admin
def horario_agregar(idn):
    f = request.form
    inicio, fin = _hora(f.get("hora_inicio")), _hora(f.get("hora_fin"))
    id_inst = entero(f.get("id_instalacion"), 1, 10**9)
    destino = redirect(url_for("admin.deporte_editar", idn=idn, _anchor="horarios"))
    if f.get("dia_semana") not in DIAS or not inicio or not fin or id_inst is None:
        flash("Completa el día, las horas y el lugar del horario.", "error")
        return destino
    if fin <= inicio:
        flash("La hora de fin debe ser después de la hora de inicio.", "error")
        return destino
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT 1 FROM deporte WHERE id_deporte = %s", (idn,))
        if not cur.fetchone():
            abort(404)
        cur.execute("SELECT 1 FROM instalacion WHERE id_instalacion = %s", (id_inst,))
        if not cur.fetchone():
            flash("Elige un lugar de la lista.", "error")
            return destino
        cur.execute(
            "SELECT d.nombre FROM horario h JOIN deporte d ON d.id_deporte = h.id_deporte "
            "WHERE h.id_instalacion = %s AND h.dia_semana = %s "
            "AND h.hora_inicio < %s AND h.hora_fin > %s LIMIT 1",
            (id_inst, f["dia_semana"], fin, inicio))
        choque = cur.fetchone()
        if choque:
            flash(f"Ese lugar ya está ocupado a esa hora por {choque['nombre']}.", "error")
            return destino
        cur.execute(
            "INSERT INTO horario (id_deporte, id_instalacion, dia_semana, hora_inicio, hora_fin) "
            "VALUES (%s, %s, %s, %s, %s)", (idn, id_inst, f["dia_semana"], inicio, fin))
        con.commit()
    flash("Listo, se agregó el horario.", "ok")
    return destino


@bp.route("/deportes/<int:idn>/horarios/quitar", methods=["POST"])
@solo_admin
def horario_quitar(idn):
    f = request.form
    inicio, fin = _hora(f.get("hora_inicio")), _hora(f.get("hora_fin"))
    id_inst = entero(f.get("id_instalacion"), 1, 10**9)
    if f.get("dia_semana") in DIAS and inicio and fin and id_inst:
        with conexion() as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM horario WHERE id_deporte = %s AND id_instalacion = %s "
                "AND dia_semana = %s AND hora_inicio = %s AND hora_fin = %s LIMIT 1",
                (idn, id_inst, f["dia_semana"], inicio, fin))
            con.commit()
        flash("Se quitó el horario.", "ok")
    return redirect(url_for("admin.deporte_editar", idn=idn, _anchor="horarios"))


# ---------- eventos ----------

@bp.route("/eventos")
@solo_admin
def eventos():
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT e.id_evento, e.nombre, e.fecha_evento, e.lugar, e.capacidad, "
            "       v.cupos_disponibles "
            "FROM evento e JOIN vista_cupos_evento v ON v.id_evento = e.id_evento "
            "ORDER BY e.fecha_evento DESC")
        lista = cur.fetchall()
    ahora = datetime.now()
    return render_template("admin/eventos.html", eventos=lista, ahora=ahora)


def leer_evento(cur, f, idn=None):
    """Valida el formulario de un evento. Devuelve (datos, mensaje_de_error)."""
    nombre = f.get("nombre", "").strip()
    lugar = f.get("lugar", "").strip()
    if not nombre or len(nombre) > 100:
        return None, "Escribe el nombre del evento (máximo 100 caracteres)."
    if not lugar or len(lugar) > 100:
        return None, "Escribe el lugar del evento (máximo 100 caracteres)."
    try:
        fecha = datetime.strptime(f.get("fecha_evento", ""), FORMATO_FECHA)
    except ValueError:
        return None, "Elige la fecha y la hora del evento."
    if idn is None and fecha < datetime.now():
        return None, "La fecha del evento no puede estar en el pasado."
    capacidad = entero(f.get("capacidad"), 1, 5000)
    if capacidad is None:
        return None, "La capacidad debe ser un número entre 1 y 5000."
    if idn and capacidad < ocupados(cur, "id_evento", idn):
        return None, "La capacidad no puede ser menor que los estudiantes ya inscritos."
    return {
        "nombre": nombre,
        "descripcion": f.get("descripcion", "").strip()[:255] or None,
        "fecha_evento": fecha,
        "lugar": lugar,
        "capacidad": capacidad,
    }, None


@bp.route("/eventos/nuevo", methods=["GET", "POST"])
@solo_admin
def evento_nuevo():
    if request.method == "POST":
        with conexion() as con:
            cur = con.cursor(dictionary=True)
            datos, error = leer_evento(cur, request.form)
            if error:
                flash(error, "error")
            else:
                cur.execute(
                    "INSERT INTO evento (nombre, descripcion, fecha_evento, lugar, capacidad) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (datos["nombre"], datos["descripcion"], datos["fecha_evento"],
                     datos["lugar"], datos["capacidad"]))
                con.commit()
                flash(f"Listo, se creó el evento {datos['nombre']}.", "ok")
                return redirect(url_for("admin.eventos"))
    return render_template("admin/evento_form.html", evento=None,
                           minimo=datetime.now().strftime(FORMATO_FECHA))


@bp.route("/eventos/<int:idn>", methods=["GET", "POST"])
@solo_admin
def evento_editar(idn):
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM evento WHERE id_evento = %s", (idn,))
        evento = cur.fetchone()
        if not evento:
            abort(404)
        if request.method == "POST":
            datos, error = leer_evento(cur, request.form, idn)
            if error:
                flash(error, "error")
            else:
                cur.execute(
                    "UPDATE evento SET nombre = %s, descripcion = %s, fecha_evento = %s, "
                    "lugar = %s, capacidad = %s WHERE id_evento = %s",
                    (datos["nombre"], datos["descripcion"], datos["fecha_evento"],
                     datos["lugar"], datos["capacidad"], idn))
                con.commit()
                flash("Listo, se guardaron los cambios del evento.", "ok")
                return redirect(url_for("admin.eventos"))
        n_ocupados = ocupados(cur, "id_evento", idn)
    return render_template("admin/evento_form.html", evento=evento, n_ocupados=n_ocupados,
                           minimo=None)


@bp.route("/eventos/<int:idn>/eliminar", methods=["POST"])
@solo_admin
def evento_eliminar(idn):
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT nombre FROM evento WHERE id_evento = %s", (idn,))
        fila = cur.fetchone()
        if not fila:
            abort(404)
        if tiene_inscripciones(cur, "id_evento", idn):
            flash(f"No se puede eliminar {fila['nombre']}: ya tiene inscripciones "
                  "registradas. Si no se va a realizar, cambia la fecha o avisa en Novedades.",
                  "error")
            return redirect(url_for("admin.evento_editar", idn=idn))
        try:
            cur.execute("DELETE FROM evento WHERE id_evento = %s", (idn,))
            con.commit()
        except IntegrityError:
            con.rollback()
            flash(f"No se pudo eliminar {fila['nombre']} porque otros datos dependen de él.", "error")
            return redirect(url_for("admin.evento_editar", idn=idn))
    flash(f"Se eliminó el evento {fila['nombre']}.", "ok")
    return redirect(url_for("admin.eventos"))


# ---------- personal (cuentas de administrador) ----------

@bp.route("/personal", methods=["GET", "POST"])
@solo_admin
def personal():
    """Crea cuentas del personal sin pedir carrera ni semestre."""
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            correo = request.form.get("correo", "").strip().lower()
            clave = request.form.get("contrasena", "")
            if not nombre or len(nombre) > 100:
                flash("Escribe el nombre completo (máximo 100 caracteres).", "error")
            elif correo.count("@") != 1 or not correo.endswith(DOMINIOS_PERSONAL) \
                    or correo.startswith("@"):
                flash("Usa un correo institucional (@unisimon.edu.co o @unisimonbolivar.edu.co).", "error")
            elif len(clave) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "error")
            else:
                try:
                    # Se usa el mismo rol que ya tiene quien crea la cuenta.
                    cur.execute(
                        "INSERT INTO usuario (nombre, correo_institucional, contrasena_hash, rol) "
                        "VALUES (%s, %s, %s, %s)",
                        (nombre, correo, generate_password_hash(clave), current_user.rol))
                    con.commit()
                except IntegrityError:
                    con.rollback()
                    flash("Ese correo ya está registrado.", "error")
                except ErrorMySQL:
                    con.rollback()
                    flash("No se pudo crear la cuenta: la base de datos exige carrera y semestre.", "error")
                else:
                    flash(f"Listo, se creó la cuenta de {nombre}. Ya puede iniciar sesión.", "ok")
                    return redirect(url_for("admin.personal"))
        cur.execute("SELECT nombre, correo_institucional FROM usuario "
                    "WHERE rol <> 'estudiante' ORDER BY nombre")
        cuentas = cur.fetchall()
    return render_template("admin/personal.html", cuentas=cuentas)


# ---------- asistencia ----------

ESTADOS_ASISTENCIA = [("inscrito", "Pendiente"), ("asistio", "Asistió"),
                      ("no_asistio", "No asistió")]
TIPOS_ASISTENCIA = {"deporte": ("id_deporte", "deporte"), "evento": ("id_evento", "evento")}


@bp.route("/asistencia")
@solo_admin
def asistencia():
    """Lista las actividades con su número de inscritos para elegir una."""
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT d.id_deporte, d.nombre, COUNT(i.id_inscripcion) AS inscritos "
            "FROM deporte d LEFT JOIN inscripcion i "
            "  ON i.id_deporte = d.id_deporte AND i.estado <> 'cancelado' "
            "GROUP BY d.id_deporte, d.nombre ORDER BY d.nombre")
        deportes_ = cur.fetchall()
        cur.execute(
            "SELECT e.id_evento, e.nombre, e.fecha_evento, COUNT(i.id_inscripcion) AS inscritos "
            "FROM evento e LEFT JOIN inscripcion i "
            "  ON i.id_evento = e.id_evento AND i.estado <> 'cancelado' "
            "GROUP BY e.id_evento, e.nombre, e.fecha_evento ORDER BY e.fecha_evento DESC")
        eventos_ = cur.fetchall()
    return render_template("admin/asistencia.html", deportes=deportes_, eventos=eventos_)


@bp.route("/asistencia/<tipo>/<int:idn>", methods=["GET", "POST"])
@solo_admin
def asistencia_detalle(tipo, idn):
    if tipo not in TIPOS_ASISTENCIA:
        abort(404)
    columna, tabla = TIPOS_ASISTENCIA[tipo]
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM {tabla} WHERE {columna} = %s", (idn,))
        actividad = cur.fetchone()
        if not actividad:
            abort(404)
        if request.method == "POST":
            validos = {e for e, _ in ESTADOS_ASISTENCIA}
            for campo, estado in request.form.items():
                if not campo.startswith("estado_") or estado not in validos:
                    continue
                id_insc = entero(campo[len("estado_"):], 1, 10**9)
                if id_insc is None:
                    continue
                cur.execute(
                    f"UPDATE inscripcion SET estado = %s WHERE id_inscripcion = %s "
                    f"AND {columna} = %s AND estado <> 'cancelado'", (estado, id_insc, idn))
            con.commit()
            flash("Listo, se guardó la asistencia.", "ok")
            return redirect(url_for("admin.asistencia_detalle", tipo=tipo, idn=idn))
        cur.execute(
            "SELECT i.id_inscripcion, i.estado, i.telefono, u.nombre, "
            "       u.correo_institucional, u.carrera, u.semestre "
            f"FROM inscripcion i JOIN usuario u ON u.id_usuario = i.id_usuario "
            f"WHERE i.{columna} = %s AND i.estado <> 'cancelado' ORDER BY u.nombre", (idn,))
        inscritos = cur.fetchall()
    conteo = {e: sum(1 for i in inscritos if i["estado"] == e) for e, _ in ESTADOS_ASISTENCIA}
    return render_template("admin/asistencia_detalle.html", tipo=tipo, actividad=actividad,
                           inscritos=inscritos, estados=ESTADOS_ASISTENCIA, conteo=conteo)


# ---------- novedades ----------

def clave_primaria(cur, tabla):
    """Nombre de la columna que identifica cada fila (se lee de la base, no se supone)."""
    cur.execute(f"SHOW KEYS FROM {tabla} WHERE Key_name = 'PRIMARY'")
    fila = cur.fetchone()
    return fila["Column_name"] if fila else None


def leer_novedad(f):
    titulo = f.get("titulo", "").strip()
    contenido = f.get("contenido", "").strip()
    if not titulo or len(titulo) > 100:
        return None, "Escribe el título (máximo 100 caracteres)."
    if len(contenido) < 5 or len(contenido) > 500:
        return None, "El contenido debe tener entre 5 y 500 caracteres."
    return {"titulo": titulo, "contenido": contenido}, None


@bp.route("/novedades")
@solo_admin
def novedades():
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        pk = clave_primaria(cur, "novedad")
        cur.execute(f"SELECT {pk} AS id, titulo, contenido, fecha_publicacion "
                    "FROM novedad ORDER BY fecha_publicacion DESC")
        lista = cur.fetchall()
    return render_template("admin/novedades.html", novedades=lista)


@bp.route("/novedades/nueva", methods=["GET", "POST"])
@solo_admin
def novedad_nueva():
    if request.method == "POST":
        datos, error = leer_novedad(request.form)
        if error:
            flash(error, "error")
        else:
            with conexion() as con:
                cur = con.cursor(dictionary=True)
                try:
                    cur.execute("INSERT INTO novedad (titulo, contenido, fecha_publicacion) "
                                "VALUES (%s, %s, NOW())", (datos["titulo"], datos["contenido"]))
                    con.commit()
                except ErrorMySQL:
                    con.rollback()
                    flash("No se pudo publicar la novedad. Revisa la tabla novedad en la base de datos.", "error")
                else:
                    flash("Listo, la novedad ya se ve en el panel de los estudiantes.", "ok")
                    return redirect(url_for("admin.novedades"))
    return render_template("admin/novedad_form.html", novedad=None)


@bp.route("/novedades/<int:idn>", methods=["GET", "POST"])
@solo_admin
def novedad_editar(idn):
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        pk = clave_primaria(cur, "novedad")
        cur.execute(f"SELECT {pk} AS id, titulo, contenido FROM novedad WHERE {pk} = %s", (idn,))
        novedad = cur.fetchone()
        if not novedad:
            abort(404)
        if request.method == "POST":
            datos, error = leer_novedad(request.form)
            if error:
                flash(error, "error")
            else:
                cur.execute(f"UPDATE novedad SET titulo = %s, contenido = %s WHERE {pk} = %s",
                            (datos["titulo"], datos["contenido"], idn))
                con.commit()
                flash("Listo, se guardaron los cambios de la novedad.", "ok")
                return redirect(url_for("admin.novedades"))
    return render_template("admin/novedad_form.html", novedad=novedad)


@bp.route("/novedades/<int:idn>/eliminar", methods=["POST"])
@solo_admin
def novedad_eliminar(idn):
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        pk = clave_primaria(cur, "novedad")
        cur.execute(f"DELETE FROM novedad WHERE {pk} = %s", (idn,))
        con.commit()
    flash("Se eliminó la novedad.", "ok")
    return redirect(url_for("admin.novedades"))


# ---------- comentarios ----------

@bp.route("/comentarios")
@solo_admin
def comentarios():
    """Comentarios que enviaron los estudiantes, del más reciente al más antiguo."""
    with conexion() as con:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT c.*, u.nombre AS autor, u.correo_institucional AS correo, "
                    "u.carrera AS carrera_autor FROM comentario c "
                    "JOIN usuario u ON u.id_usuario = c.id_usuario")
        lista = cur.fetchall()
    campo_fecha = next((k for k in (lista[0] if lista else {}) if "fecha" in k.lower()), None)
    if campo_fecha:
        lista.sort(key=lambda c: c[campo_fecha] or datetime.min, reverse=True)
    else:
        lista.reverse()
    for c in lista:
        c["fecha"] = c.get(campo_fecha) if campo_fecha else None
    return render_template("admin/comentarios.html", comentarios=lista)
