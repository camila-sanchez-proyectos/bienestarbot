"""Cuando preguntan algo que no es de deportes, Simón responde con un mensaje claro.
Ejecutar en la carpeta del proyecto:  python mensaje_fuera_de_tema.py
Se puede repetir sin problema. Guarda copia chatbot.py.bak"""
import pathlib, re, shutil

f = pathlib.Path("chatbot.py")
t = f.read_text(encoding="utf-8")
patron = re.compile(r"(def accion_no_entendi\(con, cur, u, d\):\n    return respuesta\(\n)(.*?)(\n        \[btn\(\"Explícame un deporte\")", re.S)
m = patron.search(t)
if not m:
    raise SystemExit("No encontre accion_no_entendi con el formato esperado. Ejecuta primero instalar_simon.py y avisame.")
nuevo = ('        "No puedo ayudarte con esa información. Si deseas conocer más sobre los deportes, "\n'
         '        "pregúntame aquí; estaré para ayudarte.",')
if nuevo in t:
    print("chatbot.py: ya estaba aplicado")
else:
    shutil.copy(f, "chatbot.py.bak")
    f.write_text(t[:m.start(2)] + nuevo + t[m.end(2):], encoding="utf-8")
    print("chatbot.py: mensaje actualizado")
