(function () {
  var chat = document.querySelector('.chat[data-login]');
  var pop = document.getElementById('chat-pop');
  var fab = document.getElementById('chat-fab');
  var cerrarBtn = document.getElementById('chat-close');
  var log = document.getElementById('chat-log');
  var form = document.getElementById('chat-form');
  var input = document.getElementById('chat-input');
  if (!chat || !pop || !fab || !log || !form || !input) return;

  var PLACEHOLDER = input.placeholder;
  var esperando = null;     // 'comentario' cuando el bot espera un texto libre
  var ocupado = false;
  var iniciado = false;
  var recargar = false;     // hubo una inscripción o cancelación: la página debe actualizarse
  var CLAVE = 'simon-chat';
  var historial = [];
  var ultimosBotones = null;
  function guardarChat() {
    try {
      sessionStorage.setItem(CLAVE, JSON.stringify({ h: historial.slice(-60), b: ultimosBotones, e: esperando }));
    } catch (e) { /* sin almacenamiento */ }
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;   // textContent: el texto nunca se interpreta como HTML
    return e;
  }
  function burbuja(tipo, texto) {
    log.appendChild(el('div', 'msg ' + tipo, texto));
    historial.push({ t: tipo, x: texto });
    guardarChat();
  }
  function quitarBotones() {
    log.querySelectorAll('.chips').forEach(function (n) { n.remove(); });
    ultimosBotones = null;
    guardarChat();
  }
  function botones(lista) {
    if (!lista || !lista.length) return;
    var g = el('div', 'chips');
    g.setAttribute('role', 'group');
    g.setAttribute('aria-label', 'Respuestas rápidas');
    lista.forEach(function (b) {
      var x = el('button', 'chip', b.texto);
      x.type = 'button';
      x._payload = b.payload;
      x._texto = b.texto;
      g.appendChild(x);
    });
    log.appendChild(g);
    ultimosBotones = lista;
    guardarChat();
  }
  function bajar() { log.scrollTop = log.scrollHeight; }

  /* Simón "escribe" cada respuesta poco a poco. Tocar el mensaje lo completa. */
  var reducir = false;   // siempre escribe poco a poco
  function escribir(texto) {
    return new Promise(function (resolve) {
      if (reducir || !texto) { burbuja('bot', texto); bajar(); resolve(); return; }
      var p = el('div', 'msg bot typing');
      p.setAttribute('aria-hidden', 'true');
      for (var k = 0; k < 3; k++) p.appendChild(el('span', 'punto-escribe'));
      log.appendChild(p);
      bajar();
      log.setAttribute('aria-busy', 'true');   // el lector de pantalla espera al mensaje completo
      setTimeout(function () {
        p.className = 'msg bot';
        p.removeAttribute('aria-hidden');
        p.title = 'Toca para ver el mensaje completo';
        p.textContent = '';
        var i = 0, n = texto.length;
        var paso = Math.max(1, Math.ceil(n / 110));
        var t = setInterval(function () {
          i = Math.min(n, i + paso);
          p.textContent = texto.slice(0, i);
          bajar();
          if (i >= n) {
            clearInterval(t);
            p.removeAttribute('title');
            log.removeAttribute('aria-busy');
            historial.push({ t: 'bot', x: texto });
            guardarChat();
            resolve();
          }
        }, 18);
        p.addEventListener('click', function () { i = n - paso; });
      }, Math.min(650, 250 + texto.length * 2));
    });
  }
  function escribirTodos(lista) {
    return lista.reduce(function (cadena, m) {
      return cadena.then(function () { return escribir(m); }).then(function () {
        return new Promise(function (r) { setTimeout(r, reducir ? 0 : 220); });
      });
    }, Promise.resolve());
  }

  function enviar(payload, etiqueta) {
    if (ocupado) return;
    ocupado = true;
    iniciado = true;
    quitarBotones();
    if (etiqueta) burbuja('user', etiqueta);
    bajar();

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    })
      .then(function (r) {
        return r.json().then(function (d) { return { status: r.status, d: d }; });
      })
      .then(function (res) {
        var d = res.d;
        return escribirTodos(d.mensajes || []).then(function () {
          esperando = d.esperar || null;
          guardarChat();
          input.placeholder = esperando ? 'Escribe tu comentario y envíalo' : PLACEHOLDER;
          if (d.ok) recargar = true;
          botones(d.botones);
          if (res.status === 401) {
            setTimeout(function () { window.location.href = chat.dataset.login; }, 2500);
          }
        });
      })
      .catch(function () {
        burbuja('bot', 'No pude conectarme con el servidor. Revisa que esté encendido e inténtalo de nuevo.');
        botones([{ texto: 'Menú', payload: { accion: 'menu' } }]);
      })
      .then(function () {
        ocupado = false;
        bajar();
        if (!pop.hidden) input.focus({ preventScroll: true });
      });
  }

  function abrir() {
    pop.hidden = false;
    fab.setAttribute('aria-expanded', 'true');
    if (!iniciado && !document.body.classList.contains('simon-on')) { iniciado = true; enviar({ accion: 'menu' }, null); }
    input.focus({ preventScroll: true });
  }
  function cerrar() {
    pop.hidden = true;
    fab.setAttribute('aria-expanded', 'false');
    // Si se inscribió o canceló desde el chat, se actualizan los cupos de la página.
    if (recargar) { window.location.reload(); return; }
    fab.focus({ preventScroll: true });
  }

  window.simonChatIniciar = function () { if (!iniciado) { iniciado = true; enviar({ accion: 'menu' }, null); } };
  function restaurarChat() {
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
  restaurarChat();
  fab.addEventListener('click', function () { if (pop.hidden) abrir(); else cerrar(); });
  cerrarBtn.addEventListener('click', cerrar);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !pop.hidden) cerrar();
  });

  log.addEventListener('click', function (e) {
    var b = e.target.closest('.chip');
    if (!b) return;
    if (b._payload && b._payload.url) { window.location.href = b._payload.url; return; }
    enviar(b._payload, b._texto);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var texto = input.value.trim();
    if (!texto) return;
    input.value = '';
    if (esperando === 'comentario') enviar({ accion: 'guardar_comentario', texto: texto }, texto);
    else enviar({ texto: texto }, texto);
  });
})();
