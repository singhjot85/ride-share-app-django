/**
 * navigation_state.js: Client-side navigation, tab switching, and scroll spy.
 *
 * Provides:
 * - LoadShareNav.switchTab(tabId): switches views without page reloads.
 * - Desktop scroll spy: hides center floating chip on scroll down, restores on scroll up.
 */
(function (window, document) {
    "use strict";

    var SUPPORTED_TABS = ["home", "book-corridor", "rates", "support", "profile"];
    var lastScrollY = window.pageYOffset || 0;
    var chipElement = null;

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

        // 4. Update browser URL hash
        if (updateHash && window.history && window.history.replaceState) {
            window.history.replaceState(null, "", "#" + tabId);
        }

        // 5. Scroll smoothly to top
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    /**
     * Desktop scroll spy: hide floating chip when scrolling down.
     */
    function handleScroll() {
        if (!chipElement) {
            chipElement = document.getElementById("desktop-floating-chip");
            if (!chipElement) return;
        }

        var currentScrollY = window.pageYOffset || document.documentElement.scrollTop;

        if (currentScrollY <= 80) {
            // Near top of page: always show chip
            chipElement.classList.remove("chip-hidden");
        } else if (currentScrollY > lastScrollY + 5) {
            // Scrolling down: hide chip
            chipElement.classList.add("chip-hidden");
        } else if (currentScrollY < lastScrollY - 5) {
            // Scrolling up: show chip
            chipElement.classList.remove("chip-hidden");
        }

        lastScrollY = currentScrollY;
    }

    /**
     * Initialize on DOM ready.
     */
    function init() {
        chipElement = document.getElementById("desktop-floating-chip");

        // Hash routing on initial page load
        var initialHash = window.location.hash.replace("#", "");
        if (initialHash && SUPPORTED_TABS.includes(initialHash)) {
            switchTab(initialHash, false);
        } else {
            switchTab("home", false);
        }

        // Attach scroll listener for desktop floating chip
        window.addEventListener("scroll", handleScroll, { passive: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // Expose public API
    window.LoadShareNav = {
        switchTab: switchTab,
        toggleTheme: function () {
            if (window.toggleTheme) window.toggleTheme();
        },
        applyTheme: function (theme) {
            if (window.applyTheme) window.applyTheme(theme);
        }
    };
})(window, document);
