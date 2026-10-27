/**
 * landing_interactive.js: Interactive components for the LoadShare landing page.
 *
 * Handles:
 * - Live telemetry map vs offline fallback toggle.
 * - FAQ accordion disclosure.
 */
(function (window, document) {
    "use strict";

    var isMapFallback = false;

    function toggleMapState() {
        isMapFallback = !isMapFallback;
        var liveMap = document.getElementById("corridor-live-map");
        var fallbackMap = document.getElementById("corridor-fallback-map");
        var toggleText = document.getElementById("map-toggle-text");

        if (isMapFallback) {
            if (liveMap) liveMap.style.display = "none";
            if (fallbackMap) fallbackMap.style.display = "block";
            if (toggleText) toggleText.textContent = "Preview Live Telemetry Mode";
        } else {
            if (liveMap) liveMap.style.display = "block";
            if (fallbackMap) fallbackMap.style.display = "none";
            if (toggleText) toggleText.textContent = "Toggle Offline Fallback Simulation";
        }
    }

    function toggleFaq(id) {
        var ans = document.getElementById("faq-ans-" + id);
        if (!ans) return;
        var isHidden = (ans.style.display === "none");
        ans.style.display = isHidden ? "block" : "none";
    }

    // Expose functions globally for template event handlers
    window.toggleMapState = toggleMapState;
    window.toggleFaq = toggleFaq;
})(window, document);
