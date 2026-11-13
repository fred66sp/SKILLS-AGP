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

// Galería de plantillas: un solo SVG sirve en claro y oscuro (data-surface);
// la miniatura lo incrusta y el modal lo muestra a tamaño completo.
(function () {
  "use strict";
  var gallery = document.querySelector(".template-gallery");
  if (!gallery) { return; }
  var switches = document.querySelectorAll(".surface-btn");
  var surface = gallery.getAttribute("data-surface") || "dark";

  function setSurface(next) {
    surface = next;
    gallery.setAttribute("data-surface", next);
    Array.prototype.forEach.call(gallery.querySelectorAll("svg"), function (svg) {
      svg.setAttribute("data-surface", next);
    });
    var dlg = document.getElementById("template-dialog");
    if (dlg) { dlg.setAttribute("data-surface", next); }
    Array.prototype.forEach.call(switches, function (b) {
      var on = b.getAttribute("data-surface-choice") === next;
      b.classList.toggle("is-on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  Array.prototype.forEach.call(switches, function (b) {
    b.addEventListener("click", function () { setSurface(b.getAttribute("data-surface-choice")); });
  });

  // La galería sigue al tema de la página: el botón «Tema» de la cabecera
  // también cambia las miniaturas y el modal. El conmutador de sección queda
  // como vista previa manual hasta el siguiente cambio de tema.
  var root = document.documentElement;
  function themeSurface() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
  }
  setSurface(themeSurface());
  if (window.MutationObserver) {
    new MutationObserver(function () { setSurface(themeSurface()); })
      .observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  }

  // Incrusta el SVG para que acepte data-surface; como <img> seguiría al sistema.
  Array.prototype.forEach.call(gallery.querySelectorAll(".template-thumb img"), function (img) {
    fetch(img.getAttribute("src")).then(function (r) {
      if (!r.ok) { throw new Error("sin acceso local"); }
      return r.text();
    }).then(function (text) {
      var doc = new DOMParser().parseFromString(text, "image/svg+xml");
      var svg = doc && doc.documentElement;
      if (!svg || svg.nodeName.toLowerCase() !== "svg") { throw new Error("SVG inválido"); }
      svg = document.importNode(svg, true);
      svg.setAttribute("data-surface", surface);
      img.replaceWith(svg);
    }).catch(function () { /* se queda el <img>: seguirá al sistema */ });
  });

  // Modal: mueve el mismo nodo (sin duplicar ids) y lo devuelve al cerrar.
  var dialog = null, canvas = null, title = null, opener = null, moved = null;

  function build() {
    dialog = document.createElement("dialog");
    dialog.id = "template-dialog";
    dialog.className = "template-dialog";
    dialog.setAttribute("data-surface", surface);
    dialog.innerHTML =
      '<div class="template-dialog-head"><p class="template-dialog-title"></p>' +
      '<button type="button" class="template-dialog-close" aria-label="Cerrar vista ampliada">' +
      '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>' +
      '</button></div><div class="template-dialog-canvas"></div>';
    document.body.appendChild(dialog);
    canvas = dialog.querySelector(".template-dialog-canvas");
    title = dialog.querySelector(".template-dialog-title");
    dialog.querySelector(".template-dialog-close").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (ev) { if (ev.target === dialog) { dialog.close(); } });
    dialog.addEventListener("close", function () {
      if (moved && opener) { opener.appendChild(moved); }
      moved = null;
      if (opener) { opener.focus(); opener = null; }
    });
  }

  Array.prototype.forEach.call(gallery.querySelectorAll(".template-thumb"), function (btn) {
    btn.addEventListener("click", function () {
      if (!dialog) { build(); }
      var svg = btn.querySelector("svg");
      var img = btn.querySelector("img");
      if (typeof dialog.showModal !== "function") {
        if (img) { window.open(img.src, "_blank", "noopener"); }
        return;
      }
      opener = btn;
      moved = null;
      var caption = btn.parentElement && btn.parentElement.querySelector("figcaption strong");
      title.textContent = caption ? caption.textContent : "Plantilla";
      dialog.setAttribute("data-surface", surface);
      canvas.innerHTML = "";
      if (svg) { moved = svg; canvas.appendChild(svg); }
      else if (img) {
        var big = document.createElement("img");
        big.src = img.getAttribute("src");
        big.alt = img.getAttribute("alt") || "";
        canvas.appendChild(big);
      }
      dialog.showModal();
    });
  });
})();
