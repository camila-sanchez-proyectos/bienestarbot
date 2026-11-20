import re

from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify, abort)
from flask_login import (LoginManager, UserMixin, login_user,
                         logout_user, login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import IntegrityError
from db import get_connection
from chatbot import procesar, ESTADOS, deporte_activo
from panel import cargar_panel, cargar_actividad
from info import DISCIPLINAS
from admin import bp as admin_bp

app = Flask(__name__)
app.register_blueprint(admin_bp)

@app.template_filter("nombre_corto")
def nombre_corto(nombre):
    """Primer nombre + primer apellido."""
    p = (nombre or "").split()
    if len(p) >= 4:      # Juan Carlos Perez Gomez -> Juan Perez
        return f"{p[0]} {p[2]}"
    return " ".join(p[:2])

app.secret_key = "5df0314917e2316ec9bc4efff85825fd3339da069b366e37e59541195a2ac9eb"
DOMINIO = "@unisimon.edu.co"

CARRERAS = [
    "Medicina",
    "Enfermería",
    "Fisioterapia",
    "Instrumentación Quirúrgica",
    "Derecho",
    "Psicología",
    "Trabajo Social",
    "Administración de Empresas",
    "Comercio y Negocios Internacionales",
    "Contaduría Pública",
    "Marketing y Negocios Digitales",
    "Ingeniería de Sistemas",
    "Ingeniería Multimedia",
    "Ingeniería Industrial",
    "Ingeniería de Datos e Inteligencia Artificial",
]
SEMESTRES = list(range(1, 13))
NIVELES = ["Ninguna", "Básica", "Intermedia", "Avanzada"]

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Inicia sesión para entrar."


class Usuario(UserMixin):
    def __init__(self, fila):
        self.id = fila["id_usuario"]
        self.nombre = fila["nombre"]
        self.correo = fila["correo_institucional"]
        self.rol = fila["rol"]
        self.carrera = fila.get("carrera")
        self.semestre = fila.get("semestre")


@login_manager.user_loader
def cargar_usuario(user_id):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuario WHERE id_usuario = %s", (user_id,))
    fila = cur.fetchone()
    cur.close()
    con.close()
    return Usuario(fila) if fila else None


@app.route("/")
def inicio():
    # Quien ya inició sesión ve su panel; la página pública es solo para visitantes.
    if current_user.is_authenticated:
        return redirect(url_for("admin.inicio" if current_user.rol != "estudiante" else "panel"))
    return render_template("inicio.html", disciplinas=DISCIPLINAS)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        correo = request.form["correo"].strip().lower()
        carrera = request.form.get("carrera", "")
        semestre = request.form.get("semestre", "")
        contrasena = request.form["contrasena"]

        # Regla de negocio: solo correo institucional (se valida en el servidor)
        correo_valido = (correo.count("@") == 1
                         and correo.endswith(DOMINIO)
                         and len(correo) > len(DOMINIO))

        if not correo_valido:
            flash(f"Usa tu correo institucional, que termina en {DOMINIO}.", "error")
        elif not nombre:
            flash("Escribe tu nombre completo.", "error")
        elif carrera not in CARRERAS or not semestre.isdigit() or int(semestre) not in SEMESTRES:
            flash("Elige tu carrera y tu semestre de la lista.", "error")
        elif len(contrasena) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
        else:
            con = get_connection()
            try:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO usuario (nombre, correo_institucional, "
                    "contrasena_hash, carrera, semestre) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (nombre, correo, generate_password_hash(contrasena),
                     carrera, int(semestre)),
                )
                con.commit()
            except IntegrityError:
                flash("Ese correo ya está registrado.", "error")
            else:
                flash("Cuenta creada. Ya puedes iniciar sesión.", "ok")
                return redirect(url_for("login"))
            finally:
                con.close()
    return render_template("registro.html", carreras=CARRERAS, semestres=SEMESTRES)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        contrasena = request.form["contrasena"]

        con = get_connection()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuario WHERE correo_institucional = %s", (correo,))
        fila = cur.fetchone()
        cur.close()
        con.close()

        if fila and check_password_hash(fila["contrasena_hash"], contrasena):
            login_user(Usuario(fila))
            return redirect(url_for("admin.inicio" if fila["rol"] != "estudiante" else "panel"))
        flash("Correo o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("inicio"))


@app.route("/panel")
@login_required
def panel():
    datos = cargar_panel(int(current_user.id))
    return render_template("panel.html", es_estudiante=(current_user.rol == "estudiante"),
                           estados=ESTADOS, **datos)


def _usuario_actual():
    return {"id": int(current_user.id), "nombre": current_user.nombre,
            "rol": current_user.rol}


def _resultado(datos):
    """Usa la misma lógica del chatbot y muestra el resultado como aviso."""
    try:
        texto = procesar(_usuario_actual(), datos)["mensajes"][0]
    except Exception:
        app.logger.exception("Error en el panel")
        flash("Tuve un problema para completar la acción. Inténtalo de nuevo.", "error")
    else:
        flash(texto, "ok" if texto.startswith(("Listo", "Gracias")) else "error")
    return redirect(url_for("panel", _anchor="mensajes"))


def leer_formulario(f, act, tipo):
    """Valida el formulario de inscripción. Devuelve (datos, mensaje_de_error)."""
    telefono = re.sub(r"[\s\-\+\(\)]", "", f.get("telefono", ""))
    if not re.fullmatch(r"\d{7,12}", telefono):
        return None, "Escribe un teléfono válido, solo números (de 7 a 12 dígitos)."
    datos = {"telefono": telefono,
             "observaciones": f.get("observaciones", "").strip()[:300] or None}
    if tipo == "deporte":
        if f.get("nivel") not in NIVELES:
            return None, "Elige tu nivel de experiencia."
        datos["nivel"] = f["nivel"]
        if act["ramas"]:
            if f.get("rama") not in act["ramas"]:
                return None, "Elige la rama en la que quieres participar."
            datos["rama"] = f["rama"]
        datos["interes_seleccion"] = 1 if f.get("interes_seleccion") else 0
        datos["interes_beca"] = 1 if (act["aplica_beca"] and f.get("interes_beca")) else 0
    if not f.get("declara_salud"):
        return None, "Debes confirmar que tu estado de salud te permite practicar actividad física."
    if not f.get("acepta_datos"):
        return None, "Debes autorizar el tratamiento de tus datos personales."
    datos["acepta_datos"] = 1
    return datos, None


@app.route("/inscripcion/<tipo>/<int:idn>", methods=["GET", "POST"])
@login_required
def formulario_inscripcion(tipo, idn):
    """Formulario que se llena para inscribirse a un deporte o evento."""
    if tipo not in ("deporte", "evento"):
        abort(404)
    if current_user.rol != "estudiante":
        flash("Las inscripciones son para estudiantes.", "error")
        return redirect(url_for("panel"))
    act = cargar_actividad(tipo, idn)
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
    if request.method == "POST":
        datos, error = leer_formulario(request.form, act, tipo)
        if error:
            flash(error, "error")
        else:
            return _resultado({"accion": "inscribir", "tipo": tipo, "id": idn,
                               "form": datos})
    return render_template("inscripcion.html", act=act, tipo=tipo, niveles=NIVELES)


@app.route("/inscribir", methods=["POST"])
@login_required
def inscribir():
    return _resultado({"accion": "inscribir", "tipo": request.form.get("tipo"),
                       "id": request.form.get("id")})


@app.route("/cancelar", methods=["POST"])
@login_required
def cancelar():
    return _resultado({"accion": "cancelar_ok", "id": request.form.get("id")})


@app.route("/comentario", methods=["POST"])
@login_required
def comentario():
    return _resultado({"accion": "guardar_comentario",
                       "texto": request.form.get("texto", "")})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Recibe lo que el estudiante toca o escribe y responde el chatbot."""
    if not current_user.is_authenticated:
        return jsonify({"mensajes": ["Tu sesión terminó. Inicia sesión de nuevo."],
                        "botones": [], "esperar": None}), 401
    datos = request.get_json(silent=True) or {}
    usuario = {"id": int(current_user.id), "nombre": current_user.nombre,
               "rol": current_user.rol}
    try:
        return jsonify(procesar(usuario, datos))
    except Exception:
        app.logger.exception("Error en el chatbot")
        return jsonify({"mensajes": ["Tuve un problema para responder. Inténtalo de nuevo."],
                        "botones": [], "esperar": None}), 500


if __name__ == "__main__":
    app.run(debug=True)
