"""Muestra solo primer nombre + primer apellido en el panel y la barra superior.
Ejecutar desde la carpeta del proyecto:  python aplicar_nombre_corto.py
Se puede repetir sin problema. Guarda copias .bak."""
import re, shutil, pathlib

FILTRO = '''
@app.template_filter("nombre_corto")
def nombre_corto(nombre):
    """Primer nombre + primer apellido."""
    p = (nombre or "").split()
    if len(p) >= 4:      # Juan Carlos Perez Gomez -> Juan Perez
        return f"{p[0]} {p[2]}"
    return " ".join(p[:2])
'''

app = pathlib.Path("app.py")
txt = app.read_text(encoding="utf-8")
if "nombre_corto" not in txt:
    m = re.search(r"^app\s*=\s*Flask\(.*\)\s*$", txt, re.M)
    if not m:
        raise SystemExit("No encontre la linea 'app = Flask(...)' en app.py")
    shutil.copy("app.py", "app.py.bak")
    txt = txt[:m.end()] + "\n" + FILTRO + txt[m.end():]
    app.write_text(txt, encoding="utf-8")
    print("app.py: filtro agregado")
else:
    print("app.py: ya tenia el filtro")

for nombre in ("panel.html", "base.html"):
    f = pathlib.Path("templates") / nombre
    if not f.exists():
        continue
    t = f.read_text(encoding="utf-8")
    n = re.sub(r"\{\{\s*current_user\.nombre\s*\}\}", "{{ current_user.nombre|nombre_corto }}", t)
    if n != t:
        shutil.copy(f, str(f) + ".bak")
        f.write_text(n, encoding="utf-8")
        print(f"{f}: actualizado")
    else:
        print(f"{f}: sin cambios")
