"""Simón explica los deportes (qué es, cómo se juega, qué necesitas).
Ejecutar desde la carpeta bienestarbot:  python aplicar_respuestas.py
Se puede repetir sin problema. Guarda copia chatbot.py.bak"""
import pathlib, shutil

f = pathlib.Path("chatbot.py")
t = f.read_text(encoding="utf-8")
if "conocimiento" in t:
    print("chatbot.py: ya estaba aplicado, no hice nada")
    raise SystemExit(0)

def cambiar(viejo, nuevo):
    global t
    if t.count(viejo) != 1:
        raise SystemExit("No encontre este punto en chatbot.py (no cambie nada):\n" + viejo[:90])
    t = t.replace(viejo, nuevo)

cambiar("from info import SERVICIOS, SERVICIOS_POR_ID",
        "from info import SERVICIOS, SERVICIOS_POR_ID\nimport conocimiento")

cambiar('    (("deporte", "disciplina", "ofrecen", "ofrece"), "deportes"),',
        '    (("explic", "conocer un deporte", "no se que deporte", "no se cual deporte"), "explicar_menu"),\n'
        '    (("deporte", "disciplina", "ofrecen", "ofrece"), "deportes"),')

cambiar('''    # ¿Menciona un deporte? Se prefiere el nombre más largo ("futbol americano").''',
        '''    # ¿Pregunta qué es o cómo se juega un deporte? Se le explica.
    if conocimiento.es_pregunta(t):
        clave = conocimiento.deporte_en(t)
        if clave:
            return {"accion": "explicar", "clave": clave}

    # ¿Menciona un deporte? Se prefiere el nombre más largo ("futbol americano").''')

cambiar('''def accion_no_entendi(con, cur, u, d):
    return respuesta(
        "No entendí tu mensaje. Prueba con palabras como «deportes», «horarios», "
        "«inscribirme» o «cancelar», o usa los botones.",
        menu(),
    )''', '''def accion_no_entendi(con, cur, u, d):
    return respuesta(
        "Todavía no sé responder eso. Puedo explicarte cómo se juega cada deporte, "
        "contarte horarios, entrenadores, cupos, becas, gimnasio y piscina, o inscribirte. "
        "Escríbeme algo como «¿qué es el fútbol?» o «horarios», o usa los botones.",
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
    }''')

cambiar('    "no_entendi": accion_no_entendi,',
        '    "no_entendi": accion_no_entendi,\n    "explicar": accion_explicar,\n    "explicar_menu": accion_explicar_menu,')

shutil.copy(f, "chatbot.py.bak")
f.write_text(t, encoding="utf-8")
print("chatbot.py: actualizado")
