/**
 * navigation_state.js: Client-side navigation and tab switching.
 *
 * Provides:
 * - LoadShareNav.switchTab(tabId): switches views without page reloads.
 * - LoadShareNav.updateTopBarTitle(tabId): dynamic top bar title alongside logo.
 */
(function (window, document) {
    "use strict";

    var SUPPORTED_TABS = ["home", "book-corridor", "rates", "support", "profile"];
    var TAB_TITLES = {
        "home": { en: "ROUTEWAY", hi: "लोडशेयर" },
        "book-corridor": { en: "Corridors", hi: "कॉरिडोर" },
        "rates": { en: "Rates", hi: "दरें" },
        "support": { en: "Support", hi: "सहायता" },
        "profile": { en: "Profile", hi: "प्रोफ़ाइल" }
    };

    /**
     * Get active UI language code.
     *
     * @returns {string}
     */
    function getCurrentLang() {
        if (typeof window.getActiveLanguage === "function") {
            return window.getActiveLanguage();
        }
        var match = document.cookie.match(/(^|;\s*)loadshare_lang=([^;]*)/);
        if (match && (match[2] === "en" || match[2] === "hi")) {
            return match[2];
        }
        return document.documentElement.lang === "hi" ? "hi" : "en";
    }

    /**
     * Update top bar title alongside logo according to current active tab.
     *
     * @param {string} tabId - Target tab identifier.
     */
    function updateTopBarTitle(tabId) {
        var titleEl = document.getElementById("top-bar-title");
        if (!titleEl) return;

        var titles = TAB_TITLES[tabId] || TAB_TITLES.home;
        titleEl.setAttribute("data-en", titles.en);
        titleEl.setAttribute("data-hi", titles.hi);

        var currentLang = getCurrentLang();
        titleEl.textContent = (currentLang === "hi") ? titles.hi : titles.en;
    }

    /**
     * Switch active view tab.
     *
     * @param {string} tabId - Target tab identifier.
     * @param {boolean} [updateHash=true] - Whether to update browser URL hash.
     */
    function switchTab(tabId, updateHash) {
        if (typeof updateHash === "undefined") updateHash = true;
        if (!SUPPORTED_TABS.includes(tabId)) {
            tabId = "home";
        }

        // 1. Update views visibility
        SUPPORTED_TABS.forEach(function (id) {
            var viewEl = document.getElementById("view-" + id);
            if (viewEl) {
                if (id === tabId) {
                    viewEl.classList.remove("hidden");
                    viewEl.classList.add("active");
                } else {
                    viewEl.classList.remove("active");
                    viewEl.classList.add("hidden");
                }
            }
        });

        // 2. Update Desktop Floating Chip buttons
        var chipButtons = document.querySelectorAll(".chip-nav-item");
        chipButtons.forEach(function (btn) {
            var target = btn.getAttribute("data-tab");
            if (target === tabId) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        // 3. Update Mobile Bottom Navbar buttons
        var mobileButtons = document.querySelectorAll(".bottom-nav-item");
        mobileButtons.forEach(function (btn) {
            var target = btn.getAttribute("data-tab");
            if (target === tabId) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        // 4. Update top bar title alongside logo
        updateTopBarTitle(tabId);

        // 5. Update browser URL hash
        if (updateHash && window.history && window.history.replaceState) {
            window.history.replaceState(null, "", "#" + tabId);
        }

        // 6. Scroll smoothly to top
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    /**
     * Initialize on DOM ready.
     */
    function init() {
        // Hash routing on initial page load
        var initialHash = window.location.hash.replace("#", "");
        if (initialHash && SUPPORTED_TABS.includes(initialHash)) {
            switchTab(initialHash, false);
        } else {
            switchTab("home", false);
        }
    }

    /**
     * Switch state for the Tracker Preview canvas.
     *
     * @param {'active' | 'loading' | 'empty'} state
     */
    function setDispatchState(state) {
        if (window.StateCardComponent && window.StateCardComponent.setState) {
            window.StateCardComponent.setState("tracker-preview-container", state);
        } else {
            var active = document.getElementById("state-active-dispatch");
            var skeleton = document.getElementById("state-skeleton-dispatch");
            var empty = document.getElementById("state-empty-dispatch");

            if (active) active.classList.toggle("hidden", state !== "active");
            if (skeleton) skeleton.classList.toggle("hidden", state !== "loading");
            if (empty) empty.classList.toggle("hidden", state !== "empty");
        }

        var btnActive = document.getElementById("btn-state-dispatch");
        var btnLoading = document.getElementById("btn-state-loading");
        var btnEmpty = document.getElementById("btn-state-empty");

        var activeClass = "px-2.5 py-1 rounded bg-surface-container-lowest text-primary shadow-xs font-semibold";
        var inactiveClass = "px-2.5 py-1 rounded text-on-surface-variant hover:text-primary transition-all font-semibold";

        if (btnActive) btnActive.className = (state === "active") ? activeClass : inactiveClass;
        if (btnLoading) btnLoading.className = (state === "loading") ? activeClass : inactiveClass;
        if (btnEmpty) btnEmpty.className = (state === "empty") ? activeClass : inactiveClass;
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // Expose public API
    window.LoadShareNav = {
        switchTab: switchTab,
        updateTopBarTitle: updateTopBarTitle,
        setDispatchState: setDispatchState,
        toggleTheme: function () {
            if (window.toggleTheme) window.toggleTheme();
        },
        applyTheme: function (theme) {
            if (window.applyTheme) window.applyTheme(theme);
        }
    };
})(window, document);
