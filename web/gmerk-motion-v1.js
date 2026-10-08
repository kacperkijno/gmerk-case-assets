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
/* GMERK motion v1 (08.10.2026). Zrodlo: GMERK/strona/wdrozenie/gmerk-motion-src-20261008.js, budowane do gmerk-motion-vN.js (Splitting.js MIT doklejony na poczatku).
   01 slowa naglowkow wyjezdzaja spod linii (Splitting.js), hero od razu, H2 przy wejsciu w widok
   02 case study: media odslaniaja sie od dolu przy scrollu (GSAP ScrollTrigger + Lenis, tylko strony realizacji)
   03 czerwona nic: na osi procesu (.n_os-wrapper) linia w akcencie wije sie od kropki do kropki, rysowana scrollem
   Zasady: design-system/MOTION.md. Reduced motion = nic sie nie dzieje. Gdy CDN padnie, strona zostaje jak byla. */
(function () {
  if (window.__gmMotion) return; window.__gmMotion = 1;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var EASE = 'cubic-bezier(.22,1,.36,1)', ACCENT = '#FF4A1C';

  var css = ''
    + '.gm-split .word{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .14em 0;margin:0 -.06em -.14em 0}'
    + '.gm-split .gmw{display:inline-block;transform:translateY(110%);transition:transform .9s ' + EASE + ';transition-delay:calc(var(--word-index) * 90ms)}'
    + '.gm-split.gm-in .gmw{transform:none}'
    + 'html.lenis,html.lenis body{height:auto}.lenis.lenis-smooth{scroll-behavior:auto!important}.lenis.lenis-stopped{overflow:hidden}'
    + '.gm-thread .n_os-progres-wskaznik{opacity:0!important}.gm-thread .n_od-progres{background:transparent!important}'
    + '.gm-thread-svg{position:absolute;left:0;top:0;pointer-events:none;overflow:visible;z-index:1}'
    + '.gm-thread .n_os-k-ko{position:relative;z-index:2}';
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

  /* ---------- 01 naglowki ---------- */
  var HEADS = '.hero-heading,.hero-heading-2,.n_h1-lewy,.n_h2-lewy,.n_h1-lewy-bia-y';
  function splitHeads() {
    if (!window.Splitting) return;
    var els = [].slice.call(document.querySelectorAll(HEADS)).filter(function (el) {
      return !el.closest('nav,.w-nav,#gmm') && el.textContent.trim().length;
    });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('gm-in'); io.unobserve(e.target); } });
    }, { threshold: .2, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) {
      if (!el.getAttribute('aria-label')) el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
      Splitting({ target: el, by: 'words' });
      [].forEach.call(el.querySelectorAll('.word'), function (w) {
        w.setAttribute('aria-hidden', 'true');
        w.innerHTML = '<span class="gmw">' + w.innerHTML + '</span>';
      });
      el.classList.add('gm-split');
      var hero = el.matches('.hero-heading,.hero-heading-2');
      if (hero) afterLoader(function () { el.classList.add('gm-in'); });
      else io.observe(el);
    });
  }

  /* ---------- loader ---------- */
  function load(src) {
    return new Promise(function (ok, no) {
      var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.appendChild(s);
    });
  }
  var gsapReady = null;
  function needGsap() {
    if (gsapReady) return gsapReady;
    var desktop = matchMedia('(pointer: fine)').matches;
    gsapReady = load('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js')
      .then(function () { return load('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js'); })
      .then(function () { return desktop ? load('https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js').catch(function () {}) : null; })
      .then(function () {
        gsap.registerPlugin(ScrollTrigger);
        if (desktop && window.Lenis) {
          var lenis = new Lenis({
            lerp: .1, anchors: true,
            prevent: function (n) { return !!(n.closest && n.closest('.calendly-overlay,.calendly-popup-content,#gmm,[data-lenis-prevent]')); }
          });
          window.gmLenis = lenis;
          lenis.on('scroll', ScrollTrigger.update);
          gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
          gsap.ticker.lagSmoothing(0);
          // popup Calendly: zatrzymaj plynny scroll pod spodem
          new MutationObserver(function () {
            document.querySelector('.calendly-overlay') ? lenis.stop() : lenis.start();
          }).observe(document.body, { childList: true });
        }
      });
    return gsapReady;
  }

  /* ---------- 02 case study ---------- */
  function caseReveals() {
    var root = document.querySelector('.n_sekcja-realizacja-tresc');
    if (!root) return;
    needGsap().then(function () {
      // tylko tresc case'a: figury w rich-text + duze zdjecia case'a; bez kafli innych realizacji i list CMS
      var media = [].slice.call(document.querySelectorAll('.w-richtext figure img, .w-richtext figure video, .w-richtext > div > video, [class*="n_realizacja-zdj-cie"]'));
      var seen = [];
      media.forEach(function (m) {
        if (m.closest('nav,.w-nav,footer,#gmm,.w-dyn-list .w-dyn-item .n_div-kafelek,.n_div-kafelek')) return;
        var r = m.getBoundingClientRect();
        if (r.width && r.width < 280) return;
        // zdjecia z IX Webflow: clip-path na samym elemencie (bez owijania, zeby nie ruszac ukladu i IX)
        var frame = m.hasAttribute('data-w-id') ? m : m.closest('figure');
        if (!frame) {
          var playing = m.tagName === 'VIDEO' && !m.paused;
          frame = document.createElement('div'); frame.className = 'gm-frame';
          m.parentNode.insertBefore(frame, m); frame.appendChild(m);
          if (playing) { var pr = m.play(); if (pr && pr.catch) pr.catch(function () {}); }
        }
        if (seen.indexOf(frame) > -1) return; seen.push(frame);
        if (frame !== m) frame.style.overflow = 'hidden';
        var trig = { trigger: frame, start: 'top 96%', end: 'top 50%', scrub: 1 };
        gsap.fromTo(frame, { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', ease: 'none', scrollTrigger: trig });
        if (frame !== m) gsap.fromTo(m, { scale: 1.08 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: frame, start: 'top 96%', end: 'bottom 40%', scrub: 1 } });
      });
      // obrazy dociagaja sie lazy = zmienia sie wysokosc strony
      addEventListener('load', function () { ScrollTrigger.refresh(); });
      [].forEach.call(document.images, function (i) { if (!i.complete) i.addEventListener('load', function () { ScrollTrigger.refresh(); }, { once: true }); });
    }).catch(function () {});
  }

  /* ---------- 03 czerwona nic ---------- */
  function threads() {
    var wraps = [].slice.call(document.querySelectorAll('.n_os-wrapper'));
    if (!wraps.length) return;
    needGsap().then(function () {
      wraps.forEach(function (w) {
        var dots = [].slice.call(w.querySelectorAll('.n_os-k-ko'));
        if (dots.length < 2) return;
        if (getComputedStyle(w).position === 'static') w.style.position = 'relative';
        w.classList.add('gm-thread');
        var NS = 'http://www.w3.org/2000/svg';
        var svg = document.createElementNS(NS, 'svg'); svg.setAttribute('class', 'gm-thread-svg'); svg.setAttribute('aria-hidden', 'true');
        var path = document.createElementNS(NS, 'path');
        path.setAttribute('fill', 'none'); path.setAttribute('stroke', ACCENT); path.setAttribute('stroke-width', '2');
        path.setAttribute('stroke-linecap', 'round'); path.setAttribute('vector-effect', 'non-scaling-stroke');
        var track = document.createElementNS(NS, 'path');
        track.setAttribute('fill', 'none'); track.setAttribute('stroke', '#CFCFCF'); track.setAttribute('stroke-width', '1');
        track.setAttribute('vector-effect', 'non-scaling-stroke');
        svg.appendChild(track); svg.appendChild(path); w.insertBefore(svg, w.firstChild);
        var tween = null;
        function build() {
          var wr = w.getBoundingClientRect(), W = wr.width, H = w.scrollHeight;
          svg.setAttribute('width', W); svg.setAttribute('height', H); svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
          var pts = dots.map(function (d) { var r = d.getBoundingClientRect(); return [r.left + r.width / 2 - wr.left, r.top + r.height / 2 - wr.top]; });
          var A = Math.max(10, Math.min(30, W * .05));
          var all = [[pts[0][0], 0]].concat(pts, [[pts[pts.length - 1][0], H]]);
          var d = 'M' + all[0][0].toFixed(1) + ' ' + all[0][1].toFixed(1);
          for (var i = 1; i < all.length; i++) {
            var a = all[i - 1], b = all[i], dy = b[1] - a[1], s = (i % 2 ? 1 : -1) * A;
            d += ' C' + (a[0] + s).toFixed(1) + ' ' + (a[1] + dy * .4).toFixed(1) + ' ' + (b[0] + s).toFixed(1) + ' ' + (b[1] - dy * .4).toFixed(1) + ' ' + b[0].toFixed(1) + ' ' + b[1].toFixed(1);
          }
          path.setAttribute('d', d); track.setAttribute('d', d);
          var L = path.getTotalLength();
          path.style.strokeDasharray = L;
          if (tween) { tween.scrollTrigger && tween.scrollTrigger.kill(); tween.kill(); }
          tween = gsap.fromTo(path, { strokeDashoffset: L }, { strokeDashoffset: 0, ease: 'none',
            scrollTrigger: { trigger: w, start: 'top 60%', end: 'bottom 60%', scrub: 1 } });
        }
        build();
        var to; new ResizeObserver(function () { clearTimeout(to); to = setTimeout(function () { build(); ScrollTrigger.refresh(); }, 150); }).observe(w);
      });
    }).catch(function () {});
  }

  function start() { splitHeads(); caseReveals(); threads(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
