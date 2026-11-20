"""Hace que el chat SIEMPRE escriba poco a poco y obliga al navegador a bajar el chat.js nuevo.
Ejecutar en la carpeta del proyecto:  python arreglo_escritura.py"""
import pathlib, re

js = pathlib.Path("static/js/chat.js")
t = js.read_text(encoding="utf-8")
if "escribirTodos" not in t:
    raise SystemExit("Este chat.js no tiene el efecto de escritura. Ejecuta primero instalar_simon.py")
viejo = re.search(r"var reducir = .*?;\n", t)
if viejo:
    t = t.replace(viejo.group(0), "var reducir = false;   // siempre escribe poco a poco\n", 1)
    js.write_text(t, encoding="utf-8")
    print("chat.js: el efecto ya no se apaga")
else:
    print("chat.js: ya estaba corregido")

p = pathlib.Path("templates/panel.html")
h = p.read_text(encoding="utf-8")
nuevo = re.sub(r"(filename='js/chat\.js'\)\s*\}\})(\?v=\d+)?", r"\1?v=3", h)
if nuevo != h:
    p.write_text(nuevo, encoding="utf-8")
    print("panel.html: ahora pide chat.js?v=3 (el navegador baja el nuevo)")
else:
    print("panel.html: sin cambios" if "chat.js" in h else "panel.html: no encontre la linea de chat.js")
