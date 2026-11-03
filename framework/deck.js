/* deck.js — reveal.js bootstrap shared by every generated deck. */

(function () {
  "use strict";

  var isPrint = /print-pdf/gi.test(window.location.search);

  Reveal.initialize({
    // 16:9 design canvas. All deck.css sizing is absolute px against this box.
    width: 1280,
    height: 720,
    margin: 0.04,
    minScale: 0.2,
    maxScale: 1.6,

    hash: true,
    slideNumber: "c/t",
    showSlideNumber: "speaker",
    history: false,
    center: false,
    transition: "slide",
    transitionSpeed: "fast",
    backgroundTransition: "fade",
    controls: true,
    controlsTutorial: false,
    controlsLayout: "bottom-right",
    progress: true,
    overview: true,
    hideInactiveCursor: true,
    hideCursorTime: 3000,
    pdfSeparateFragments: false,
    pdfMaxPagesPerSlide: 1,

    plugins: [RevealNotes, RevealHighlight, RevealZoom, RevealSearch],
  });

  // --- Light/dark toggle, persisted per browser -----------------------------
  var KEY = "deck-theme";
  var root = document.documentElement;

  var saved = null;
  try {
    saved = localStorage.getItem(KEY);
  } catch (e) {
    /* storage blocked (private mode, file://) — fall back to the baked-in theme */
  }
  if (saved) root.setAttribute("data-theme", saved);

  function toggleTheme() {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem(KEY, next);
    } catch (e) {
      /* non-fatal: the toggle still applies for this page view */
    }
  }

  Reveal.addKeyBinding(
    { keyCode: 84, key: "T", description: "Toggle light / dark" },
    toggleTheme
  );

  // --- Export helper --------------------------------------------------------
  // Shift+P jumps to reveal's print stylesheet so the browser print dialog
  // produces one PDF page per slide.
  Reveal.addKeyBinding(
    { keyCode: 80, key: "Shift+P", description: "Print / export to PDF" },
    function () {
      var u = new URL(window.location.href);
      u.searchParams.set("print-pdf", "");
      window.location.href = u.toString();
    }
  );

  if (isPrint) {
    document.documentElement.setAttribute("data-theme", "light");
  }
})();
