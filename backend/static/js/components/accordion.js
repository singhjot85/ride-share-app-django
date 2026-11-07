/**
 * accordion.js: Modular client-side controller for accordion components.
 *
 * Provides:
 * - Single-open exclusivity when data-allow-multiple="false"
 * - Dispatches 'accordion:toggle' events
 */
(function (window, document) {
    "use strict";

    function initAccordion(container) {
        var allowMultiple = container.getAttribute("data-allow-multiple") !== "false";
        var items = container.querySelectorAll(".accordion-item");

        items.forEach(function (item) {
            item.addEventListener("toggle", function () {
                var isOpen = item.open;

                if (isOpen && !allowMultiple) {
                    // Close other items in the same container
                    items.forEach(function (otherItem) {
                        if (otherItem !== item && otherItem.open) {
                            otherItem.open = false;
                        }
                    });
                }

                // Dispatch custom event
                var event = new CustomEvent("accordion:toggle", {
                    detail: {
                        containerId: container.id,
                        item: item,
                        isOpen: isOpen
                    }
                });
                container.dispatchEvent(event);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        var accordions = document.querySelectorAll(".accordion-container");
        accordions.forEach(initAccordion);
    });

    window.AccordionComponent = {
        init: initAccordion
    };

})(window, document);
