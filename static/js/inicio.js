(function () {
  /* Chat de ejemplo */
  var log = document.getElementById('chat-log');
  var MENU = ['Ver deportes', 'Inscribirme', 'Cancelar'];
  var SPORTS = ['Fútbol', 'Baloncesto', 'Voleibol', 'Taekwondo'];
  var current = 'Baloncesto';
  var enrolled = null;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function bubble(kind, text) { log.appendChild(el('div', 'msg ' + kind, text)); }
  function chips(list) {
    var g = el('div', 'chips');
    g.setAttribute('role', 'group');
    g.setAttribute('aria-label', 'Respuestas rápidas');
    list.forEach(function (t) {
      var b = el('button', 'chip', t);
      b.type = 'button';
      b.dataset.q = t;
      g.appendChild(b);
    });
    log.appendChild(g);
  }
  function turn(user, bot, list) {
    log.querySelectorAll('.chips').forEach(function (n) { n.remove(); });
    if (user) bubble('user', user);
    bubble('bot', bot);
    chips(list);
    log.scrollTop = log.scrollHeight;
  }
  function reply(q) {
    if (q === 'Ver deportes' || q === 'Ver otros deportes')
      return turn(q, 'Estos son los deportes disponibles. Elige uno para ver su descripción, instructor, horario y cupo.', SPORTS);
    if (q === 'Inscribirme')
      return turn(q, '¿En qué deporte o evento quieres inscribirte?', SPORTS);
    if (q === 'Cancelar') {
      if (!enrolled) return turn(q, 'Todavía no tienes inscripciones activas. Primero elige un deporte para inscribirte.', MENU);
      return turn(q, '¿Quieres cancelar tu inscripción? Al cancelarla, el cupo queda libre para otro estudiante.', ['Cancelar ' + enrolled, 'Volver al menú']);
    }
    if (q.indexOf('Cancelar ') === 0) {
      var was = q.slice(9);
      enrolled = null;
      return turn(q, 'Listo, cancelé tu inscripción en ' + was + '.', MENU);
    }
    if (q === 'Sí, inscribirme') {
      enrolled = current;
      return turn(q, 'Listo, quedaste inscrito en ' + current + '. Puedes cancelar cuando quieras desde este chat.', MENU);
    }
    if (q === 'Probar con cupo lleno')
      return turn(q, 'El cupo de ' + current + ' está lleno, por eso no puedo inscribirte. Elige otro deporte o evento.', SPORTS.filter(function (s) { return s !== current; }));
    if (q === 'Volver al menú')
      return turn(q, '¿Qué quieres hacer?', MENU);
    if (SPORTS.indexOf(q) !== -1) {
      current = q;
      return turn(q, q + ': te muestro su descripción, el instructor, el horario y el lugar. Hay cupo disponible. ¿Quieres inscribirte?', ['Sí, inscribirme', 'Probar con cupo lleno', 'Ver otros deportes']);
    }
  }
  bubble('bot', 'Hola, soy Simón. ¿Qué quieres hacer hoy?');
  turn('Ver deportes', 'Estos son los deportes disponibles. Elige uno para ver su descripción, instructor, horario y cupo.', SPORTS);
  log.addEventListener('click', function (e) {
    var b = e.target.closest('.chip');
    if (b) reply(b.dataset.q);
  });

  /* Índice lateral: marca la sección visible */
  try {
    var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && byId[en.target.id]) {
          links.forEach(function (l) { l.removeAttribute('aria-current'); });
          byId[en.target.id].setAttribute('aria-current', 'true');
        }
      });
    }, { rootMargin: '-20% 0px -65% 0px' });
    Object.keys(byId).forEach(function (id) {
      var s = document.getElementById(id);
      if (s) io.observe(s);
    });
  } catch (err) {}
})();
