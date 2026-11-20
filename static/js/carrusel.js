(function () {
  'use strict';
  var raiz = document.querySelector('.carrusel');
  if (!raiz) return;

  var vp = raiz.querySelector('.car-viewport');
  var slides = [].slice.call(raiz.querySelectorAll('.car-slide'));
  var btnAnt = raiz.querySelector('.car-ant');
  var btnSig = raiz.querySelector('.car-sig');
  var btnPausa = raiz.querySelector('.car-pausa');
  var cajaPuntos = raiz.querySelector('.car-puntos');
  var N = slides.length;
  if (!vp || !N) return;

  var INTERVALO = 4500;
  var reducir = false;   // el avance automático siempre está activo
  var actual = 0, pausaUsuario = reducir, pausaTemp = false, visible = true, modal = null, timer = null;
  raiz.style.setProperty('--car-intervalo', INTERVALO + 'ms');

  function dos(n) { return (n < 10 ? '0' : '') + n; }

  /* Puntos de navegación */
  var puntos = !cajaPuntos ? [] : slides.map(function (s, i) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'car-punto';
    b.setAttribute('aria-label', 'Ir al afiche ' + (i + 1) + ' de ' + N);
    b.addEventListener('click', function () { ir(i); });
    cajaPuntos.appendChild(b);
    return b;
  });

  function marcar(i) {
    actual = i;
    puntos.forEach(function (p, k) {
      p.classList.toggle('on', k === i);
      if (k === i) p.setAttribute('aria-current', 'true'); else p.removeAttribute('aria-current');
    });
  }

  function ir(i) {
    i = (i + N) % N;
    vp.scrollTo({ left: slides[i].offsetLeft, behavior: reducir ? 'auto' : 'smooth' });
    marcar(i);
    programar();
  }

  function indiceVisible() {
    var max = vp.scrollWidth - vp.clientWidth;
    if (vp.scrollLeft >= max - 2) return N - 1;
    var mejor = 0, dist = Infinity;
    slides.forEach(function (s, k) {
      var d = Math.abs(s.offsetLeft - vp.scrollLeft);
      if (d < dist) { dist = d; mejor = k; }
    });
    return mejor;
  }

  /* Avance automático */
  function corriendo() {
    return !pausaUsuario && !pausaTemp && visible && !document.hidden && !modal;
  }
  function programar() {
    clearTimeout(timer);
    raiz.classList.remove('corre');
    if (!corriendo()) return;
    void raiz.offsetWidth;                 // reinicia la barra de progreso
    raiz.classList.add('corre');
    timer = setTimeout(function () {
      var max = vp.scrollWidth - vp.clientWidth;
      ir(vp.scrollLeft >= max - 2 ? 0 : actual + 1);
    }, INTERVALO);
  }

  /* Cuando el usuario desliza a mano */
  var finScroll = null;
  vp.addEventListener('scroll', function () {
    clearTimeout(finScroll);
    finScroll = setTimeout(function () {
      /* Si llegó adonde se le pidió (aunque el final de la tira lo frene), se respeta lo elegido */
      var esperado = Math.min(slides[actual].offsetLeft, vp.scrollWidth - vp.clientWidth);
      if (Math.abs(vp.scrollLeft - esperado) > 3) { marcar(indiceVisible()); programar(); }
    }, 120);
  }, { passive: true });

  if (btnAnt) btnAnt.addEventListener('click', function () { ir(actual - 1); });
  if (btnSig) btnSig.addEventListener('click', function () { ir(actual + 1); });
  vp.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); ir(actual - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); ir(actual + 1); }
  });

  /* Pausa explícita (el movimiento automático siempre se puede detener) */
  function pintarPausa() {
    btnPausa.setAttribute('aria-pressed', pausaUsuario ? 'true' : 'false');
    btnPausa.setAttribute('aria-label', pausaUsuario ? 'Reanudar el avance automático' : 'Pausar el avance automático');
  }
  if (btnPausa) {
    btnPausa.addEventListener('click', function () { pausaUsuario = !pausaUsuario; pintarPausa(); programar(); });
    pintarPausa();
  }

  /* Solo se detiene cuando la pestaña no se ve o el carrusel está fuera de la pantalla.
     El mouse, el foco y los clics ya NO lo pausan. */
  document.addEventListener('visibilitychange', programar);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; programar(); }, { threshold: 0.25 }).observe(raiz);
  }

  /* Afiche ampliado */
  function abrirModal(i) {
    if (!modal) {
      modal = document.createElement('dialog');
      modal.className = 'car-modal';
      modal.setAttribute('aria-label', 'Afiche ampliado');
      modal.innerHTML =
        '<img alt="">' +
        '<div class="car-modal-barra">' +
        '<button type="button" class="car-btn m-ant" aria-label="Afiche anterior"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>' +
        '<span class="car-modal-cuenta"></span>' +
        '<button type="button" class="car-btn m-sig" aria-label="Afiche siguiente"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>' +
        '<button type="button" class="car-btn m-cerrar" aria-label="Cerrar"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' +
        '</div>';
      document.body.appendChild(modal);
      modal.querySelector('.m-ant').addEventListener('click', function () { verModal(modal._i - 1); });
      modal.querySelector('.m-sig').addEventListener('click', function () { verModal(modal._i + 1); });
      modal.querySelector('.m-cerrar').addEventListener('click', function () { modal.close(); });
      modal.addEventListener('click', function (e) { if (e.target === modal) modal.close(); });
      modal.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') verModal(modal._i - 1);
        if (e.key === 'ArrowRight') verModal(modal._i + 1);
      });
      modal.addEventListener('close', function () {
        var m = modal; modal = null; m.remove();
        slides[actual].querySelector('.car-ver').focus({ preventScroll: true });
        programar();
      });
    }
    verModal(i);
    modal.showModal();
    programar();
  }
  function verModal(i) {
    i = (i + N) % N;
    modal._i = i;
    var img = slides[i].querySelector('img');
    var g = modal.querySelector('img');
    g.src = img.currentSrc || img.src;
    g.alt = img.alt;
    marcar(i);
    vp.scrollTo({ left: slides[i].offsetLeft, behavior: 'auto' });
  }
  slides.forEach(function (s, i) {
    s.querySelector('.car-ver').addEventListener('click', function () { abrirModal(i); });
  });

  marcar(0);
  programar();
})();
