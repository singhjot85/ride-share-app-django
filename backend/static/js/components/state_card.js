/**
 * state_card.js: Modular client-side controller for multi-state containers & cards.
 *
 * Provides:
 * - StateCardComponent.setState(containerId, stateName): activates specific state panel.
 */
(function (window, document) {
    "use strict";

    /**
     * Switch visible state panel inside a state container.
     *
     * @param {string} containerId - Target container ID.
     * @param {string} targetState - State identifier to show (e.g. "default", "skeleton", "empty", "capacity", "error").
     */
    function setState(containerId, targetState) {
        var container = document.getElementById(containerId);
        if (!container) return;

        var panels = container.querySelectorAll(".state-panel");
        panels.forEach(function (panel) {
            var panelState = panel.getAttribute("data-state");
            if (panelState === targetState) {
                panel.classList.remove("hidden");
                panel.classList.add("active");
            } else {
                panel.classList.add("hidden");
                panel.classList.remove("active");
            }
        });

        container.setAttribute("data-active-state", targetState);

        // Dispatch component lifecycle event
        var event = new CustomEvent("statecard:change", {
            detail: {
                containerId: containerId,
                state: targetState
            }
        });
        container.dispatchEvent(event);
    }

    // Public API
    window.StateCardComponent = {
        setState: setState
    };

})(window, document);
