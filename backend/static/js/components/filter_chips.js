/**
 * filter_chips.js: Modular client-side controller for filter chips and pill switchers.
 *
 * Provides:
 * - Declarative click and selection handling across chip groups
 * - Programmatic selection via FilterChipsComponent.setActive(containerId, value)
 * - Emits 'filter:change' CustomEvents on the container
 * - Invokes configured data-on-change callback function
 */
(function (window, document) {
    "use strict";

    function resolveHandler(path) {
        if (!path) return null;
        var parts = path.split(".");
        var target = window;
        for (var i = 0; i < parts.length; i++) {
            if (target && typeof target === "object" && parts[i] in target) {
                target = target[parts[i]];
            } else {
                return null;
            }
        }
        return typeof target === "function" ? target : null;
    }

    function setActive(containerOrId, value, triggerCallback) {
        var container = typeof containerOrId === "string" ? document.getElementById(containerOrId) : containerOrId;
        if (!container) return;

        var chips = container.querySelectorAll(".filter-chip");
        var activeChip = null;

        chips.forEach(function (chip) {
            var chipVal = chip.getAttribute("data-value");
            var isMatch = String(chipVal) === String(value);
            chip.setAttribute("aria-selected", isMatch ? "true" : "false");
            chip.classList.toggle("is-active", isMatch);
            if (isMatch) {
                activeChip = chip;
            }
        });

        if (activeChip && triggerCallback !== false) {
            // Dispatch custom event
            var event = new CustomEvent("filter:change", {
                bubbles: true,
                detail: {
                    containerId: container.id,
                    value: value,
                    chip: activeChip
                }
            });
            container.dispatchEvent(event);

            // Execute configured callback if present
            var callbackName = container.getAttribute("data-on-change");
            if (callbackName) {
                var handler = resolveHandler(callbackName);
                if (handler) {
                    handler(value, activeChip);
                }
            }
        }
    }

    function initFilterChips(container) {
        if (container.getAttribute("data-filter-chips-initialized")) return;
        container.setAttribute("data-filter-chips-initialized", "true");

        var chips = container.querySelectorAll(".filter-chip");
        chips.forEach(function (chip) {
            chip.addEventListener("click", function () {
                var value = chip.getAttribute("data-value");
                setActive(container, value, true);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        var groups = document.querySelectorAll("[data-filter-chips]");
        groups.forEach(initFilterChips);
    });

    window.FilterChipsComponent = {
        init: initFilterChips,
        setActive: setActive
    };

})(window, document);
