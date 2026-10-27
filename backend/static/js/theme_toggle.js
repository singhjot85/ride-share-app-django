/**
 * theme_toggle.js: Dark/Light appearance theme switcher & FOUC prevention for LoadShare.
 *
 * Sourced in <head> to execute synchronously before <body> paints, preventing
 * Flash of Unstyled Content (FOUC).
 *
 * Implements:
 * - Immediate theme resolution (cookie -> localStorage -> sessionStorage -> OS preference).
 * - Multi-layer persistence (cookie, localStorage, sessionStorage) with loadshare_ prefix.
 * - Icon synchronization and 250ms debounce guard.
 */
(function (window, document) {
    "use strict";

    var lastToggleTime = 0;

    /**
     * Resolve user's active theme preference.
     *
     * @returns {'light' | 'dark'}
     */
    function getStoredTheme() {
        try {
            var cookieMatch = document.cookie.match(/(^|;\s*)loadshare_theme=([^;]*)/);
            if (cookieMatch) {
                return decodeURIComponent(cookieMatch[2]);
            }
            var storageTheme = localStorage.getItem("loadshare_theme") || sessionStorage.getItem("loadshare_theme");
            if (storageTheme) {
                return storageTheme;
            }
            if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
                return "dark";
            }
        } catch (e) {
            console.debug("Theme preference detection error:", e);
        }
        return "light";
    }

    /**
     * Update toggle button icon in the top header.
     *
     * @param {'light' | 'dark'} theme
     */
    function updateThemeIcon(theme) {
        var iconEl = document.querySelector("#theme-toggle-btn .theme-toggle-icon, #theme-toggle-btn .material-symbols-outlined");
        if (iconEl) {
            iconEl.textContent = (theme === "dark") ? "light_mode" : "dark_mode";
        }
    }

    /**
     * Apply theme to DOM elements and synchronize storage and icon.
     *
     * @param {'light' | 'dark'} theme
     */
    function applyTheme(theme) {
        var html = document.documentElement;
        var body = document.body;

        if (theme === "dark") {
            html.classList.add("dark");
            html.setAttribute("data-theme", "dark");
            if (body) {
                body.classList.add("dark");
                body.setAttribute("data-theme", "dark");
            }
        } else {
            html.classList.remove("dark");
            html.setAttribute("data-theme", "light");
            if (body) {
                body.classList.remove("dark");
                body.setAttribute("data-theme", "light");
            }
        }

        try {
            localStorage.setItem("loadshare_theme", theme);
            sessionStorage.setItem("loadshare_theme", theme);
        } catch (e) {
            console.debug("Theme storage write error:", e);
        }

        // Set 1-year persistent cookie for SSR and devtools inspection
        document.cookie = "loadshare_theme=" + encodeURIComponent(theme) + "; path=/; max-age=31536000; SameSite=Lax";

        updateThemeIcon(theme);
    }

    /**
     * Toggle theme between light and dark with a 250ms debounce guard.
     */
    function toggleTheme() {
        var now = Date.now();
        if (now - lastToggleTime < 250) {
            return;
        }
        lastToggleTime = now;

        var html = document.documentElement;
        var isDark = html.classList.contains("dark") || html.getAttribute("data-theme") === "dark";
        var nextTheme = isDark ? "light" : "dark";
        applyTheme(nextTheme);
    }

    // 1. Immediate Execution in <head> to prevent FOUC
    var initialTheme = getStoredTheme();
    if (initialTheme === "dark") {
        document.documentElement.classList.add("dark");
        document.documentElement.setAttribute("data-theme", "dark");
    } else {
        document.documentElement.classList.remove("dark");
        document.documentElement.setAttribute("data-theme", "light");
    }

    // 2. Synchronize toggle button icon when DOM is ready
    function onDomReady() {
        updateThemeIcon(initialTheme);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", onDomReady);
    } else {
        onDomReady();
    }

    // 3. Expose global API
    window.toggleTheme = toggleTheme;
    window.applyTheme = applyTheme;
    window.getStoredTheme = getStoredTheme;
})(window, document);
