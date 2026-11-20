"""La conversación con Simón se conserva mientras la sesión esté abierta y se reinicia al cerrar sesión.
Ejecutar dentro de la carpeta del proyecto:  python instalar_conversacion.py
Requiere haber ejecutado antes instalar_bienvenida.py. Se puede repetir. Guarda copia chat.js.bak2"""
import base64, zlib, pathlib, shutil

SIMON_JS = "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"

raiz = pathlib.Path.cwd()
if not (raiz / "app.py").exists() or not (raiz / "static").is_dir():
    raise SystemExit("Esta no es la carpeta del proyecto (no veo app.py ni static).\nEntra con:  cd %USERPROFILE%\\bienestarbot")
print("Carpeta del proyecto:", raiz)

(raiz / "static/js/simon.js").write_bytes(zlib.decompress(base64.b64decode(SIMON_JS)))
print("  escrito: static/js/simon.js")

f = raiz / "static/js/chat.js"
t = f.read_text(encoding="utf-8")
if "guardarChat" in t:
    print("chat.js: ya estaba aplicado")
else:
    estado = """  var CLAVE = 'simon-chat';
  var historial = [];
  var ultimosBotones = null;
  function guardarChat() {
    try {
      sessionStorage.setItem(CLAVE, JSON.stringify({ h: historial.slice(-60), b: ultimosBotones, e: esperando }));
    } catch (e) { /* sin almacenamiento */ }
  }
"""
    restaurar = """  function restaurarChat() {
    var d = null;
    try { d = JSON.parse(sessionStorage.getItem(CLAVE) || 'null'); } catch (e) { d = null; }
    if (!d || !d.h || !d.h.length) return;
    d.h.forEach(function (m) {
      log.appendChild(el('div', 'msg ' + (m.t === 'user' ? 'user' : 'bot'), String(m.x)));
    });
    historial = d.h.slice();
    iniciado = true;
    esperando = d.e || null;
    if (esperando) input.placeholder = 'Escribe tu comentario y envíalo';
    if (d.b && d.b.length) botones(d.b);
    bajar();
  }
"""
    cambios = [
        ("  var recargar = false;", None),  # se maneja abajo (la línea lleva un comentario)
        ("  function burbuja(tipo, texto) { log.appendChild(el('div', 'msg ' + tipo, texto)); }",
         "  function burbuja(tipo, texto) {\n    log.appendChild(el('div', 'msg ' + tipo, texto));\n    historial.push({ t: tipo, x: texto });\n    guardarChat();\n  }"),
        ("    log.querySelectorAll('.chips').forEach(function (n) { n.remove(); });\n  }",
         "    log.querySelectorAll('.chips').forEach(function (n) { n.remove(); });\n    ultimosBotones = null;\n    guardarChat();\n  }"),
        ("    log.appendChild(g);\n  }",
         "    log.appendChild(g);\n    ultimosBotones = lista;\n    guardarChat();\n  }"),
        ("            p.removeAttribute('title');\n            log.removeAttribute('aria-busy');\n            resolve();",
         "            p.removeAttribute('title');\n            log.removeAttribute('aria-busy');\n            historial.push({ t: 'bot', x: texto });\n            guardarChat();\n            resolve();"),
        ("          esperando = d.esperar || null;",
         "          esperando = d.esperar || null;\n          guardarChat();"),
        ("  fab.addEventListener('click', function () { if (pop.hidden) abrir(); else cerrar(); });",
         restaurar + "  restaurarChat();\n  fab.addEventListener('click', function () { if (pop.hidden) abrir(); else cerrar(); });"),
    ]
    # el estado se declara justo después de la línea de 'recargar'
    linea = [l for l in t.split("\n") if l.startswith("  var recargar = false;")]
    if len(linea) != 1:
        raise SystemExit("No encontre 'var recargar' en chat.js (no cambie nada).")
    t = t.replace(linea[0], linea[0] + "\n" + estado.rstrip("\n"), 1)
    for viejo, nuevo in cambios[1:]:
        if t.count(viejo) != 1:
            raise SystemExit("No encontre este punto en chat.js (no cambie nada):\n" + viejo[:90])
        t = t.replace(viejo, nuevo)
    shutil.copy(f, str(f) + ".bak2")
    f.write_text(t, encoding="utf-8")
    print("chat.js: actualizado")

print("\n===== VERIFICACION =====")
print("guarda la conversacion :", "SI" if "guardarChat" in f.read_text(encoding="utf-8") else "NO")
print("se reinicia sin sesion :", "SI" if "reiniciarSimon" in (raiz / "static/js/simon.js").read_text(encoding="utf-8") else "NO")
print("\nReinicia el servidor (Ctrl+C y python app.py) y recarga con Ctrl+F5.")
