/* Comportamiento común de las páginas de skill: tema, copiar código,
   volver arriba y entrada por scroll. */
(function () {
  "use strict";

  var root = document.documentElement;
  var STORAGE_KEY = (root.getAttribute("data-skill") || "skills") + ":prefs";

  var COPY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
  var CHECK_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';

  function updateThemeLabel() {
    var btn = document.getElementById("theme-toggle");
    if (!btn) { return; }
    var dark = root.getAttribute("data-theme") === "dark";
    btn.setAttribute("aria-label", dark ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  }

  function applyTheme(theme) {
    if (theme !== "dark" && theme !== "light") { theme = "light"; }
    root.setAttribute("data-theme", theme);
    updateThemeLabel();
  }

  var prefs = {};
  try { prefs = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); } catch (e) { prefs = {}; }

  var initialTheme = prefs.theme;
  if (initialTheme !== "dark" && initialTheme !== "light") {
    initialTheme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  applyTheme(initialTheme);

  function savePrefs() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); } catch (e) {}
  }

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      prefs.theme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(prefs.theme);
      savePrefs();
    });
  }

  // El botón de copiar no se escribe en el marcado: se crea aquí para que
  // añadir un bloque de código no obligue a recordar su botón.
  document.querySelectorAll(".code").forEach(function (block) {
    if (block.querySelector(".copy")) { return; }
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy";
    btn.innerHTML = COPY_ICON + "<span>Copiar</span>";
    btn.setAttribute("aria-label", "Copiar");
    block.appendChild(btn);

    btn.addEventListener("click", function () {
      var pre = block.querySelector("pre");
      var code = (pre && (pre.querySelector("code") || pre)) || null;
      if (!code) { return; }
      var done = function () {
        btn.classList.add("copied");
        btn.innerHTML = CHECK_ICON + "<span>Copiado</span>";
        btn.setAttribute("aria-label", "Copiado");
        setTimeout(function () {
          btn.classList.remove("copied");
          btn.innerHTML = COPY_ICON + "<span>Copiar</span>";
          btn.setAttribute("aria-label", "Copiar");
        }, 1600);
      };
      var text = code.textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta);
        done();
      }
    });
  });

  if ("IntersectionObserver" in window) {
    var links = {};
    document.querySelectorAll(".toc a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          Object.keys(links).forEach(function (id) { links[id].classList.remove("active"); });
          if (links[entry.target.id]) { links[entry.target.id].classList.add("active"); }
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });
    document.querySelectorAll("main section").forEach(function (s) { observer.observe(s); });
  }
})();

(function () {
  "use strict";
  var toTop = document.getElementById("to-top");
  if (!toTop) { return; }
  function update() { toTop.classList.toggle("is-visible", window.scrollY > 480); }
  window.addEventListener("scroll", update, { passive: true });
  update();
})();

(function () {
  "use strict";
  // Entrada por scroll, misma línea que el catálogo: cascada escalonada en
  // los bloques múltiples y los listados, fade simple en el resto; los que
  // llegan juntos se renumeran en --d. Sin observer, todo queda visible.
  var cascade = document.querySelectorAll(".card, .step, .flow-step, .qa, section > ul.tight > li");
  var fades = document.querySelectorAll(".section-head, .section > p, .note, .code, .table-wrap");
  if (!cascade.length && !fades.length) { return; }
  if (!("IntersectionObserver" in window)) { return; }
  var observer = new IntersectionObserver(function (entries) {
    entries.filter(function (e) { return e.isIntersecting; })
      .sort(function (a, b) {
        return parseFloat(a.target.style.getPropertyValue("--d")) - parseFloat(b.target.style.getPropertyValue("--d"));
      })
      .forEach(function (entry, i) {
        entry.target.style.setProperty("--d", i);
        entry.target.classList.add("is-in");
        observer.unobserve(entry.target);
      });
  }, { threshold: 0, rootMargin: "0px 0px -8% 0px" });
  cascade.forEach(function (block, i) {
    block.style.setProperty("--d", i);
    block.classList.add("is-ready");
    observer.observe(block);
  });
  fades.forEach(function (block) {
    block.style.setProperty("--d", 0);
    block.classList.add("is-ready");
    observer.observe(block);
  });
})();
