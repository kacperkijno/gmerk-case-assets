/*! Splitting.js 1.0.6 | MIT | Stephen Shaw */
!function(n,t){"object"==typeof exports&&"undefined"!=typeof module?module.exports=t():"function"==typeof define&&define.amd?define(t):n.Splitting=t()}(this,function(){"use strict"
var u=document,l=u.createTextNode.bind(u)
function d(n,t,e){n.style.setProperty(t,e)}function f(n,t){return n.appendChild(t)}function p(n,t,e,r){var i=u.createElement("span")
return t&&(i.className=t),e&&(!r&&i.setAttribute("data-"+t,e),i.textContent=e),n&&f(n,i)||i}function h(n,t){return n.getAttribute("data-"+t)}function m(n,t){return n&&0!=n.length?n.nodeName?[n]:[].slice.call(n[0].nodeName?n:(t||u).querySelectorAll(n)):[]}function o(n){for(var t=[];n--;)t[n]=[]
return t}function g(n,t){n&&n.some(t)}function c(t){return function(n){return t[n]}}var a={}
function n(n,t,e,r){return{by:n,depends:t,key:e,split:r}}function e(n){return function t(e,n,r){var i=r.indexOf(e)
if(-1==i)r.unshift(e),g(a[e].depends,function(n){t(n,e,r)})
else{var u=r.indexOf(n)
r.splice(i,1),r.splice(u,0,e)}return r}(n,0,[]).map(c(a))}function t(n){a[n.by]=n}function v(n,r,i,u,o){n.normalize()
var c=[],a=document.createDocumentFragment()
u&&c.push(n.previousSibling)
var s=[]
return m(n.childNodes).some(function(n){if(!n.tagName||n.hasChildNodes()){if(n.childNodes&&n.childNodes.length)return s.push(n),void c.push.apply(c,v(n,r,i,u,o))
var t=n.wholeText||"",e=t.trim()
e.length&&(" "===t[0]&&s.push(l(" ")),g(e.split(i),function(n,t){t&&o&&s.push(p(a,"whitespace"," ",o))
var e=p(a,r,n)
c.push(e),s.push(e)})," "===t[t.length-1]&&s.push(l(" ")))}else s.push(n)}),g(s,function(n){f(a,n)}),n.innerHTML="",f(n,a),c}var s=0
var i="words",r=n(i,s,"word",function(n){return v(n,"word",/\s+/,0,1)}),y="chars",w=n(y,[i],"char",function(n,e,t){var r=[]
return g(t[i],function(n,t){r.push.apply(r,v(n,"char","",e.whitespace&&t))}),r})
function b(t){var f=(t=t||{}).key
return m(t.target||"[data-splitting]").map(function(a){var s=a["🍌"]
if(!t.force&&s)return s
s=a["🍌"]={el:a}
var n=e(t.by||h(a,"splitting")||y),l=function(n,t){for(var e in t)n[e]=t[e]
return n}({},t)
return g(n,function(n){if(n.split){var t=n.by,e=(f?"-"+f:"")+n.key,r=n.split(a,l,s)
e&&(i=a,c=(o="--"+e)+"-index",g(u=r,function(n,t){Array.isArray(n)?g(n,function(n){d(n,c,t)}):d(n,c,t)}),d(i,o+"-total",u.length)),s[t]=r,a.classList.add(t)}var i,u,o,c}),a.classList.add("splitting"),s})}function N(n,t,e){var r=m(t.matching||n.children,n),i={}
return g(r,function(n){var t=Math.round(n[e]);(i[t]||(i[t]=[])).push(n)}),Object.keys(i).map(Number).sort(x).map(c(i))}function x(n,t){return n-t}b.html=function(n){var t=(n=n||{}).target=p()
return t.innerHTML=n.content,b(n),t.outerHTML},b.add=t
var T=n("lines",[i],"line",function(n,t,e){return N(n,{matching:e[i]},"offsetTop")}),L=n("items",s,"item",function(n,t){return m(t.matching||n.children,n)}),k=n("rows",s,"row",function(n,t){return N(n,t,"offsetTop")}),A=n("cols",s,"col",function(n,t){return N(n,t,"offsetLeft")}),C=n("grid",["rows","cols"]),M="layout",S=n(M,s,s,function(n,t){var e=t.rows=+(t.rows||h(n,"rows")||1),r=t.columns=+(t.columns||h(n,"columns")||1)
if(t.image=t.image||h(n,"image")||n.currentSrc||n.src,t.image){var i=m("img",n)[0]
t.image=i&&(i.currentSrc||i.src)}t.image&&d(n,"background-image","url("+t.image+")")
for(var u=e*r,o=[],c=p(s,"cell-grid");u--;){var a=p(c,"cell")
p(a,"cell-inner"),o.push(a)}return f(n,c),o}),H=n("cellRows",[M],"row",function(n,t,e){var r=t.rows,i=o(r)
return g(e[M],function(n,t,e){i[Math.floor(t/(e.length/r))].push(n)}),i}),O=n("cellColumns",[M],"col",function(n,t,e){var r=t.columns,i=o(r)
return g(e[M],function(n,t){i[t%r].push(n)}),i}),j=n("cells",["cellRows","cellColumns"],"cell",function(n,t,e){return e[M]})
return t(r),t(w),t(T),t(L),t(k),t(A),t(C),t(S),t(H),t(O),t(j),b})

;
/* GMERK motion v2 (08.10.2026). Zrodlo: GMERK/strona/wdrozenie/gmerk-motion-src-20261008.js, budowane do gmerk-motion-vN.js
   (Splitting.js MIT doklejony na poczatku + ";" - bez srednika ta funkcja sie nie odpala).
   01 slowa naglowkow wyjezdzaja spod linii (Splitting.js); IX Webflow na tych naglowkach wylaczone, zeby sie nie gryzly
   02 case study: kazde zdjecie/wideo w tresci odslania sie od dolu przy wejsciu w widok (+ Lenis na desktopie)
   03 czerwona nic na osi procesu (.n_os-wrapper): kropka przy tytule kazdego kroku, krok pojawia sie, gdy nic do niego dojdzie
   Zasady: design-system/MOTION.md. Reduced motion = nic sie nie dzieje (zostaje IX Webflow). Gdy CDN padnie, strona jak byla. */
(function () {
  if (window.__gmMotion) return; window.__gmMotion = 2;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var EASE = 'cubic-bezier(.22,1,.36,1)', ACCENT = '#FF4A1C', READ = .55; // READ = wysokosc ekranu, na ktorej idzie koncowka nici

  var css = ''
    /* 01: nasze slowa; IX Webflow (opacity/transform/blur inline) zneutralizowane na podzielonych naglowkach */
    + '.gm-split{opacity:1!important;transform:none!important;filter:none!important}'
    + '.gm-split .gm-box{display:block}.gm-split .whitespace{display:inline}'
    + '.gm-split .word{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .14em 0;margin:0 -.06em -.14em 0}'
    + '.gm-split .gmw{display:inline-block;transform:translateY(110%);transition:transform .9s ' + EASE + ';transition-delay:calc(var(--word-index) * 90ms)}'
    + '.gm-split.gm-in .gmw{transform:none}'
    /* 02 */
    + '.gm-rv{clip-path:inset(100% 0 0 0);transition:clip-path 1.3s ' + EASE + '}'
    + '.gm-rv.gm-in{clip-path:inset(0 0 0 0)}'
    + 'html.lenis,html.lenis body{height:auto}.lenis.lenis-smooth{scroll-behavior:auto!important}.lenis.lenis-stopped{overflow:hidden}'
    /* 03 */
    + '.gm-thread .n_os-progres-wskaznik,.gm-thread .n_os-k-ko{opacity:0!important}.gm-thread .n_od-progres{background:transparent!important}'
    + '.gm-thread-svg{position:absolute;left:0;top:0;pointer-events:none;overflow:visible;z-index:1}'
    + '.gm-thread .n_os-grid{opacity:0!important;transform:translateY(16px)!important;filter:none!important;transition:opacity .7s ' + EASE + ',transform .7s ' + EASE + '!important}'
    + '.gm-thread .n_os-grid.gm-on{opacity:1!important;transform:none!important}'
    + '.gm-thread .n_os-grid *{filter:none!important}'
    + '.gm-dot{transform-box:fill-box;transform-origin:center;transform:scale(0);transition:transform .45s ' + EASE + '}'
    + '.gm-dot.gm-on{transform:scale(1)}';
  var st = document.createElement('style'); st.id = 'gm-motion'; st.textContent = css; document.head.appendChild(st);

  /* loader strony (.wgrywanie, IX): hero rusza dopiero, gdy zniknie; max 6 s */
  function afterLoader(fn) {
    var t0 = Date.now();
    (function tick() {
      var l = document.querySelector('.wgrywanie'), s = l && getComputedStyle(l);
      var gone = !l || s.display === 'none' || s.visibility === 'hidden' || +s.opacity < .05 || l.getBoundingClientRect().height < 2;
      if (gone || Date.now() - t0 > 6000) setTimeout(fn, 120); else requestAnimationFrame(tick);
    })();
  }

  /* wejscie w widok; elementy juz nad ekranem (odswiezenie w polowie strony) pokazuja sie od razu */
  // sprawdzanie pozycji przy scrollu zamiast IntersectionObserver: IO gubil elementy w kontenerach przycinanych przez IX Webflow
  function onEnter(els, fn, line) {
    var left = els.slice(), queued = false;
    function check() {
      queued = false;
      var lim = innerHeight * (line || .88);
      left = left.filter(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < lim && (r.height > 0 || r.top < 0)) { fn(el); return false; }
        return true;
      });
      if (!left.length) { removeEventListener('scroll', q); removeEventListener('resize', q); }
    }
    function q() { if (!queued) { queued = true; requestAnimationFrame(check); } }
    addEventListener('scroll', q, { passive: true }); addEventListener('resize', q); addEventListener('load', q);
    setTimeout(check, 60);
  }

  /* ---------- 01 naglowki ---------- */
  var HEADS = '.hero-heading,.hero-heading-2,.n_h1-lewy,.n_h2-lewy,.n_h1-lewy-bia-y';
  function splitHeads() {
    if (!window.Splitting) return;
    var els = [].slice.call(document.querySelectorAll(HEADS)).filter(function (el) {
      return !el.closest('nav,.w-nav,#gmm') && el.textContent.trim().length;
    });
    var later = [];
    els.forEach(function (el) {
      if (!el.getAttribute('aria-label')) el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
      Splitting({ target: el, by: 'words' });
      [].forEach.call(el.querySelectorAll('.word'), function (w) {
        w.setAttribute('aria-hidden', 'true');
        w.innerHTML = '<span class="gmw">' + w.innerHTML + '</span>';
      });
      // naglowki w Webflow bywaja flexem: wtedy kazde slowo to osobny element flex i znikaja spacje -> jeden wewnetrzny span
      var box = document.createElement('span'); box.className = 'gm-box';
      while (el.firstChild) box.appendChild(el.firstChild);
      el.appendChild(box);
      el.classList.add('gm-split');
      if (el.matches('.hero-heading,.hero-heading-2')) afterLoader(function () { el.classList.add('gm-in'); });
      else later.push(el);
    });
    onEnter(later, function (el) { el.classList.add('gm-in'); }, .85);
  }

  /* ---------- Lenis (tylko desktop, tylko strony z case/osia) ---------- */
  var lenisOn = false;
  function smooth() {
    if (lenisOn || !matchMedia('(pointer: fine)').matches) return; lenisOn = true;
    var s = document.createElement('script'); s.src = 'https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js';
    s.onload = function () {
      if (!window.Lenis) return;
      var lenis = new Lenis({
        lerp: .1, anchors: true,
        prevent: function (n) { return !!(n.closest && n.closest('.calendly-overlay,.calendly-popup-content,#gmm,[data-lenis-prevent]')); }
      });
      window.gmLenis = lenis;
      (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(performance.now());
      new MutationObserver(function () { document.querySelector('.calendly-overlay') ? lenis.stop() : lenis.start(); })
        .observe(document.body, { childList: true });
    };
    document.head.appendChild(s);
  }

  /* ---------- 02 case study ---------- */
  function caseReveals() {
    var root = document.querySelector('.n_sekcja-realizacja-tresc');
    if (!root) return;
    smooth();
    var media = [].slice.call(document.querySelectorAll('.n_sekcja-realizacja-tresc img, .n_sekcja-realizacja-tresc video')).filter(function (m) {
      if (m.closest('a,nav,.w-nav,footer,#gmm,.n_div-kafelek,.n_div-realizacja-video,.n_gridrealizacje_zebrane,.n_div-ikona')) return false;
      var w = m.getBoundingClientRect().width || m.offsetWidth;
      return !(w && w < 200);
    });
    media.forEach(function (m) { m.classList.add('gm-rv'); });
    onEnter(media, function (m) { m.classList.add('gm-in'); });
  }

  /* ---------- 03 czerwona nic ---------- */
  function threads() {
    var wraps = [].slice.call(document.querySelectorAll('.n_os-wrapper'));
    if (!wraps.length) return;
    smooth();
    wraps.forEach(function (w) {
      var rows = [].slice.call(w.querySelectorAll('.n_os-grid'));
      if (rows.length < 2) return;
      if (getComputedStyle(w).position === 'static') w.style.position = 'relative';
      w.classList.add('gm-thread');
      var NS = 'http://www.w3.org/2000/svg';
      var svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'gm-thread-svg'); svg.setAttribute('aria-hidden', 'true');
      function mk(tag, at) { var e = document.createElementNS(NS, tag); for (var k in at) e.setAttribute(k, at[k]); svg.appendChild(e); return e; }
      var track = mk('path', { fill: 'none', stroke: '#CFCFCF', 'stroke-width': 1 });
      var path = mk('path', { fill: 'none', stroke: ACCENT, 'stroke-width': 2, 'stroke-linecap': 'round' });
      var dots = rows.map(function () { return mk('circle', { r: 5, fill: '#000', 'class': 'gm-dot' }); });
      w.insertBefore(svg, w.firstChild);

      var L = 0, marks = [], lut = [], cur = 0, H = 0;
      function build() {
        var wr = w.getBoundingClientRect(); H = w.scrollHeight;
        svg.setAttribute('width', wr.width); svg.setAttribute('height', H); svg.setAttribute('viewBox', '0 0 ' + wr.width + ' ' + H);
        // kropka: x = srodek kolumny linii, y = srodek pierwszej linii tytulu kroku.
        // Tytul jest sticky (top:50vh), wiec y liczymy od komorki .n_os-lewa (naturalna pozycja), nie od samego tytulu
        var pts = rows.map(function (r) {
          var col = r.querySelector('.n_os-linia') || r.querySelector('.n_os-k-ko') || r, cr = col.getBoundingClientRect();
          var t = r.querySelector('.n_h3-prawy') || r, cell = r.querySelector('.n_os-lewa') || t, tr = cell.getBoundingClientRect();
          var cs = getComputedStyle(t), lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2 || 40;
          return [cr.left + cr.width / 2 - wr.left, tr.top - wr.top + lh / 2];
        });
        var A = Math.max(8, Math.min(26, wr.width * .045));
        var all = [[pts[0][0], 0]].concat(pts, [[pts[pts.length - 1][0], H]]);
        var d = 'M' + all[0][0].toFixed(1) + ' 0';
        for (var i = 1; i < all.length; i++) {
          var a = all[i - 1], b = all[i], dy = b[1] - a[1], s = (i % 2 ? 1 : -1) * A;
          d += ' C' + (a[0] + s).toFixed(1) + ' ' + (a[1] + dy * .4).toFixed(1) + ' ' + (b[0] + s).toFixed(1) + ' ' + (b[1] - dy * .4).toFixed(1) + ' ' + b[0].toFixed(1) + ' ' + b[1].toFixed(1);
        }
        path.setAttribute('d', d); track.setAttribute('d', d);
        L = path.getTotalLength(); path.style.strokeDasharray = L;
        // tablica y -> dlugosc (sciezka idzie monotonicznie w dol)
        lut = []; for (var k = 0; k <= 400; k++) { var l = L * k / 400; lut.push([path.getPointAtLength(l).y, l]); }
        marks = pts.map(function (p, j) { dots[j].setAttribute('cx', p[0]); dots[j].setAttribute('cy', p[1]); return lenAtY(p[1]); });
        cur = Math.min(cur, L);
      }
      function lenAtY(y) {
        if (y <= lut[0][0]) return 0;
        for (var i = 1; i < lut.length; i++) if (lut[i][0] >= y) {
          var a = lut[i - 1], b = lut[i], f = (y - a[0]) / ((b[0] - a[0]) || 1); return a[1] + (b[1] - a[1]) * f;
        }
        return L;
      }
      var running = false;
      function frame() {
        var target = lenAtY(innerHeight * READ - w.getBoundingClientRect().top);
        cur += (target - cur) * .14; if (Math.abs(target - cur) < .5) cur = target;
        path.style.strokeDashoffset = L - cur;
        for (var j = 0; j < marks.length; j++) if (cur >= marks[j] - 2 && !rows[j].classList.contains('gm-on')) {
          rows[j].classList.add('gm-on'); dots[j].classList.add('gm-on');
        }
        if (running) requestAnimationFrame(frame);
      }
      build(); path.style.strokeDashoffset = L;
      new IntersectionObserver(function (es) {
        var vis = es[0].isIntersecting;
        if (vis && !running) { running = true; requestAnimationFrame(frame); } else if (!vis) running = false;
      }, { rootMargin: '30% 0px 30% 0px' }).observe(w);
      // juz przewiniete ponizej osi (odswiezenie strony) = wszystko pokazane
      if (w.getBoundingClientRect().bottom < innerHeight * READ) { cur = L; frame(); }
      var to; new ResizeObserver(function () { clearTimeout(to); to = setTimeout(build, 150); }).observe(w);
    });
  }

  function start() { splitHeads(); caseReveals(); threads(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
