/**
 * language_toggle.js: Bilingual UI language switcher for LoadShare.
 *
 * Implements:
 * - Layer 1: Instant DOM text node swapping without page refresh.
 * - Layer 2: Cookie persistence (loadshare_lang, django_language) & API synchronization.
 */
(function (window, document) {
    "use strict";

    var SUPPORTED_LANGS = ["en", "hi"];

    function getActiveLanguage() {
        var match = document.cookie.match(/(^|;\s*)loadshare_lang=([^;]*)/);
        if (match && SUPPORTED_LANGS.includes(match[2])) {
            return match[2];
        }
        var rootLang = document.documentElement.lang;
        return SUPPORTED_LANGS.includes(rootLang) ? rootLang : "en";
    }

    function setLanguage(lang) {
        if (!SUPPORTED_LANGS.includes(lang)) return;

        // 1. Layer 1: Update UI indicator styling
        var enIndicator = document.getElementById("lang-en");
        var hiIndicator = document.getElementById("lang-hi");
        if (enIndicator && hiIndicator) {
            enIndicator.className = (lang === "en") ? "lang-active" : "lang-inactive";
            hiIndicator.className = (lang === "hi") ? "lang-active" : "lang-inactive";
        }

        // 2. Layer 1: Swap all .lang-text nodes immediately
        var nodes = document.querySelectorAll(".lang-text");
        nodes.forEach(function (el) {
            var translated = el.getAttribute("data-" + lang);
            if (translated) {
                el.textContent = translated;
            }
        });

        // Update html lang attribute
        document.documentElement.lang = lang;

        // 3. Layer 2: Cookie persistence (1 year duration)
        var cookieVal = lang + "; path=/; max-age=31536000; SameSite=Lax";
        document.cookie = "loadshare_lang=" + cookieVal;
        document.cookie = "django_language=" + cookieVal;

        // 4. Layer 2: Background sync to set-language endpoint
        if (window.fetch) {
            fetch("/set-language/?lang=" + encodeURIComponent(lang), {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            }).catch(function (err) {
                console.debug("Language persistence sync error:", err);
            });
        }
    }

    function toggleLanguage() {
        var current = getActiveLanguage();
        setLanguage(current === "en" ? "hi" : "en");
    }

    // Expose functions globally for template event handlers
    window.setLanguage = setLanguage;
    window.toggleLanguage = toggleLanguage;

    document.addEventListener("DOMContentLoaded", function () {
        var toggleBtns = document.querySelectorAll("[data-action='toggle-lang']");
        toggleBtns.forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                toggleLanguage();
            });
        });
    });
})(window, document);
