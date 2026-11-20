(function () {
  'use strict';
  var script = document.currentScript;
  var IMG = script && script.src ? new URL('../img/simon.png', script.src).href : '/static/img/simon.png';
  var IMG_BIENVENIDA = script && script.src ? new URL('../img/simon-bienvenida.png', script.src).href : '/static/img/simon-bienvenida.png';

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function leer(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function guardar(k) { try { sessionStorage.setItem(k, '1'); } catch (e) { /* sin almacenamiento */ } }
  function simon(ancho) {
    var w = el('span', 'simon');
    var img = el('img');
    img.src = IMG; img.alt = 'Simón, el asistente de Deportes';
    if (ancho) img.width = ancho;
    w.appendChild(img);
    w.appendChild(el('span', 'sombra'));
    w.lastChild.setAttribute('aria-hidden', 'true');
    return w;
  }

  /* ----- 1) Visitante (sin sesión): Simón aparece flotando, sin tapar la página ----- */
  function visitante() {
    var dock = el('div', 'simon-dock');
    dock.hidden = true;

    var globo = el('div', 'simon-globo');
    globo.setAttribute('role', 'status');
    globo.appendChild(el('span', null, 'Hola, soy Simón. ¿En qué puedo ayudarte?'));
    var x = el('button', 'cerrar', '×');
    x.type = 'button'; x.setAttribute('aria-label', 'Cerrar el saludo');
    x.addEventListener('click', function () { globo.remove(); });
    globo.appendChild(x);
    if (leer('simon-visitante-globo')) globo = null;
    else dock.appendChild(globo);

    var menu = el('div', 'simon-globo simon-menu');
    menu.id = 'simon-menu';
    menu.hidden = true;
    menu.appendChild(el('span', null, '¡Hola! Soy Simón, el asistente de Deportes.'));
    menu.appendChild(el('small', null, 'Te cuento de deportes, horarios, entrenadores y becas.'));
    var ops = el('div', 'simon-opciones');
    var ver = el('button', 'op primaria', 'Ver deportes');
    ver.type = 'button';
    ver.addEventListener('click', function () {
      var d = document.querySelector('#disciplinas');
      if (d) d.scrollIntoView({ behavior: 'smooth' });
      alternar(false);
    });
    ops.appendChild(ver);
    var login = document.querySelector('a[href*="/login"]');
    if (login) { var a1 = el('a', 'op', 'Iniciar sesión'); a1.href = login.href; ops.appendChild(a1); }
    var reg = document.querySelector('a[href*="/registro"]');
    if (reg) { var a2 = el('a', 'op', 'Crear mi cuenta'); a2.href = reg.href; ops.appendChild(a2); }
    menu.appendChild(ops);
    dock.appendChild(menu);

    var boton = el('button', 'simon-fab');
    boton.type = 'button';
    boton.setAttribute('aria-label', 'Hablar con Simón');
    boton.setAttribute('aria-controls', 'simon-menu');
    boton.setAttribute('aria-expanded', 'false');
    boton.appendChild(simon());
    var punto = el('span', 'punto', '1');
    punto.setAttribute('aria-hidden', 'true');
    boton.appendChild(punto);
    dock.appendChild(boton);

    function alternar(abrir) {
      menu.hidden = !abrir;
      boton.setAttribute('aria-expanded', abrir ? 'true' : 'false');
      dock.classList.toggle('abierto', abrir);
      guardar('simon-visitante-globo');
      if (abrir) { var g = dock.querySelector('.simon-globo:not(.simon-menu)'); if (g) g.remove(); }
    }
    boton.addEventListener('click', function () { alternar(menu.hidden); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { alternar(false); boton.focus(); } });

    document.body.appendChild(dock);
    /* Aparece un momento después de cargar la página, no antes */
    setTimeout(function () { dock.hidden = false; }, 1200);
  }

  /* ----- 2) Lanzador flotante: reemplaza el botón de ayuda del chat ----- */
  function lanzador() {
    var fab = document.getElementById('chat-fab');
    var pop = document.getElementById('chat-pop');
    if (!fab || !pop) return false;
    document.body.classList.add('simon-on');

    var dock = el('div', 'simon-dock');
    if (!leer('simon-globo-cerrado')) {
      var globo = el('div', 'simon-globo');
      globo.setAttribute('role', 'status');
      globo.appendChild(el('span', null, 'Hola, soy Simón. ¿En qué puedo ayudarte?'));
      var x = el('button', 'cerrar', '×');
      x.type = 'button'; x.setAttribute('aria-label', 'Cerrar el saludo');
      x.addEventListener('click', function () { guardar('simon-globo-cerrado'); globo.remove(); });
      globo.appendChild(x);
      dock.appendChild(globo);
    }
    var boton = el('button', 'simon-fab');
    boton.type = 'button';
    boton.setAttribute('aria-label', 'Abrir el chat con Simón');
    boton.setAttribute('aria-controls', 'chat-pop');
    boton.appendChild(simon());
    var punto = el('span', 'punto', '1');
    punto.setAttribute('aria-hidden', 'true');
    boton.appendChild(punto);
    boton.addEventListener('click', function () { fab.click(); });
    dock.appendChild(boton);
    document.body.appendChild(dock);

    /* Tarjeta de bienvenida: aparece cada vez que se abre el chat */
    var tarjeta = null;
    var seccion = pop.querySelector('.chat');
    var cab = seccion && seccion.querySelector('.chat-head');
    var comp = seccion && seccion.querySelector('.composer');
    var campo = pop.querySelector('input[type="text"], input:not([type])');
    var formulario = pop.querySelector('form');
    if (seccion && cab && comp) {
      tarjeta = el('div', 'simon-tarjeta');
      tarjeta.hidden = true;
      tarjeta.setAttribute('role', 'region');
      tarjeta.setAttribute('aria-label', 'Bienvenida de Simón');
      var int = el('div', 'int');
      var fig = el('img');
      fig.src = IMG_BIENVENIDA;
      fig.alt = 'Simón saluda, rodeado de los deportes de Bienestar';
      int.appendChild(fig);
      int.appendChild(el('h3', null, '¡Hola! Soy Simón'));
      int.appendChild(el('p', null, '¿Tienes dudas sobre deportes, horarios o actividades? ¡Pregúntame!'));
      var hablemos = el('button', 'simon-hablemos', '¡Hablemos!');
      hablemos.type = 'button';
      int.appendChild(hablemos);
      tarjeta.appendChild(int);
      seccion.appendChild(tarjeta);

      var ocultarTarjeta = function (iniciar) {
        if (tarjeta.hidden) return;
        tarjeta.hidden = true;
        if (iniciar && window.simonChatIniciar) window.simonChatIniciar();
        if (campo) campo.focus({ preventScroll: true });
      };
      hablemos.addEventListener('click', function () { ocultarTarjeta(true); });
      if (campo) campo.addEventListener('input', function () { ocultarTarjeta(false); });
      if (formulario) formulario.addEventListener('submit', function () { ocultarTarjeta(false); });
    }
    function mostrarTarjeta() {
      if (!tarjeta) return;
      tarjeta.style.top = cab.offsetHeight + 'px';
      tarjeta.style.bottom = comp.offsetHeight + 'px';
      /* La imagen se ajusta para que el título, el texto y el botón siempre se vean completos */
      var libre = seccion.offsetHeight - cab.offsetHeight - comp.offsetHeight;
      tarjeta.style.setProperty('--simon-img', Math.max(110, Math.min(240, libre - 200)) + 'px');
      tarjeta.hidden = false;
      setTimeout(function () { if (!tarjeta.hidden) hablemos.focus({ preventScroll: true }); }, 60);
    }

    function sincronizar() {
      var abierto = fab.getAttribute('aria-expanded') === 'true';
      dock.classList.toggle('abierto', abierto);
      boton.setAttribute('aria-expanded', abierto ? 'true' : 'false');
      if (abierto) { guardar('simon-globo-cerrado'); mostrarTarjeta(); }
      else if (tarjeta) tarjeta.hidden = true;
    }
    new MutationObserver(sincronizar).observe(fab, { attributes: true, attributeFilter: ['aria-expanded'] });
    sincronizar();

    /* El chat también habla como Simón */
    var titulo = pop.querySelector('.chat-title');
    if (titulo) titulo.textContent = 'Simón';
    var medalla = pop.querySelector('.chat-head .medal');
    if (medalla) { medalla.classList.add('simon-medalla'); medalla.setAttribute('aria-label', 'Simón'); }
    var seccion = pop.querySelector('.chat');
    if (seccion) seccion.setAttribute('aria-label', 'Chat con Simón');
    return true;
  }

  /* Sin sesión (portada, login, registro): se borra la conversación y lo que Simón recuerda.
     Así, al cerrar sesión todo empieza de cero y Simón vuelve a saludar. */
  function reiniciarSimon() {
    try {
      Object.keys(sessionStorage).forEach(function (k) {
        if (k.indexOf('simon-') === 0) sessionStorage.removeItem(k);
      });
    } catch (e) { /* sin almacenamiento */ }
  }

  function iniciar() {
    if (!(document.getElementById('chat-fab') && document.getElementById('chat-pop'))) reiniciarSimon();
    if (!lanzador() && document.getElementById('disciplinas')) visitante();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
