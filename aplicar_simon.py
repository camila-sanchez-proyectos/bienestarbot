"""Conecta a Simón con el proyecto. Ejecutar desde la carpeta bienestarbot:
    python aplicar_simon.py
Se puede repetir sin problema. Guarda copias .bak."""
import pathlib, shutil

def guardar(f, texto):
    shutil.copy(f, str(f) + ".bak")
    f.write_text(texto, encoding="utf-8")

# 1) base.html: carga los estilos y el script de Simón
base = pathlib.Path("templates/base.html")
if not base.exists():
    raise SystemExit("No encuentro templates/base.html. Ejecuta esto dentro de la carpeta bienestarbot.")
t = base.read_text(encoding="utf-8")
if "simon.css" in t:
    print("base.html: ya estaba aplicado")
else:
    css = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/simon.css\') }}">\n'
    js = '<script src="{{ url_for(\'static\', filename=\'js/simon.js\') }}" defer></script>\n'
    if t.count("</head>") != 1 or t.count("</body>") != 1:
        raise SystemExit("base.html no tiene un unico </head> y </body>. No cambie nada; avisame.")
    t = t.replace("</head>", css + "</head>").replace("</body>", js + "</body>")
    guardar(base, t)
    print("base.html: actualizado")

# 2) chatbot.py: el saludo del chat dice «Soy Simón»
bot = pathlib.Path("chatbot.py")
t = bot.read_text(encoding="utf-8")
if "Soy BienestarBot, el asistente" in t:
    guardar(bot, t.replace("Soy BienestarBot, el asistente", "Soy Simón, el asistente"))
    print("chatbot.py: saludo actualizado")
else:
    print("chatbot.py: sin cambios (ya dice Simón o el texto es otro)")
