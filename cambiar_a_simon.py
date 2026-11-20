"""El asistente se llama Simón en todo el sitio (chat, textos y ejemplo de la portada).
Ejecutar en la carpeta del proyecto:  python cambiar_a_simon.py
Se puede repetir sin problema. Guarda copias .bak. El nombre del sitio (BienestarBot en el
logo y el título de las pestañas) no se toca."""
import pathlib, shutil

CAMBIOS = {
    "templates/inicio.html": [
        ('<span class="medal" role="img" aria-label="BienestarBot"></span>',
         '<span class="medal simon-medalla" role="img" aria-label="Simón"></span>'),
        ('aria-label="Ejemplo de conversación con BienestarBot"', 'aria-label="Ejemplo de conversación con Simón"'),
        ('<div class="chat-title">BienestarBot</div>', '<div class="chat-title">Simón</div>'),
        ('BienestarBot te muestra los deportes', 'Simón, el asistente de Deportes, te muestra los deportes'),
    ],
    "templates/panel.html": [
        ('<span class="medal" role="img" aria-label="BienestarBot"></span>',
         '<span class="medal simon-medalla" role="img" aria-label="Simón"></span>'),
        ('aria-label="Chat con BienestarBot"', 'aria-label="Chat con Simón"'),
        ('<div class="chat-title">BienestarBot</div>', '<div class="chat-title">Simón</div>'),
        ('abre el chat con el botón «¿Necesitas ayuda?».',
         'pregúntale a Simón, el gatito de la esquina inferior derecha: te explica los deportes y te ayuda a inscribirte.'),
        ('<span>¿Necesitas ayuda?</span>', '<span>Hablar con Simón</span>'),
    ],
    "chatbot.py": [
        ('"""Chatbot de BienestarBot (Deportes)', '"""Simón, el chatbot de Deportes de BienestarBot'),
    ],
}
# El texto de ejemplo de la portada vive en inicio.js: ahí todo «BienestarBot» es el asistente.
GLOBAL = {"static/js/inicio.js": ("BienestarBot", "Simón")}

def guardar(f, texto):
    b = pathlib.Path(str(f) + ".bak")
    if not b.exists():
        shutil.copy(f, b)
    f.write_text(texto, encoding="utf-8")

for ruta, lista in CAMBIOS.items():
    f = pathlib.Path(ruta)
    if not f.exists():
        print(f"{ruta}: no existe, lo salto"); continue
    t = f.read_text(encoding="utf-8"); hechos = 0
    for viejo, nuevo in lista:
        if viejo in t:
            t = t.replace(viejo, nuevo); hechos += 1
    if hechos:
        guardar(f, t); print(f"{ruta}: {hechos} cambio(s)")
    else:
        print(f"{ruta}: sin cambios (ya estaba o el texto es otro)")

for ruta, (viejo, nuevo) in GLOBAL.items():
    f = pathlib.Path(ruta)
    if not f.exists():
        print(f"{ruta}: no existe, lo salto"); continue
    t = f.read_text(encoding="utf-8")
    n = t.count(viejo)
    if n:
        guardar(f, t.replace(viejo, nuevo)); print(f"{ruta}: {n} cambio(s)")
    else:
        print(f"{ruta}: sin cambios")
print("\nReinicia el servidor (Ctrl+C y python app.py) y recarga con Ctrl+F5.")
