/**
 * Sticky Action Bar Controller
 * Manages visibility transitions and summary content for pinned bottom docks.
 */
(function () {
    "use strict";

    function showStickyBar(id, summaryText) {
        var targetId = id || "stickyBottomBar";
        var el = document.getElementById(targetId);
        if (!el) return;

        if (summaryText) {
            var summaryEl = el.querySelector(".sticky-bar-summary, #pinnedTruckSummary");
            if (summaryEl) {
                summaryEl.textContent = summaryText;
            }
        }

        el.classList.remove("translate-y-full");

        var event = new CustomEvent("ls:stickybar:shown", { detail: { id: targetId } });
        document.dispatchEvent(event);
    }

    function hideStickyBar(id) {
        var targetId = id || "stickyBottomBar";
        var el = document.getElementById(targetId);
        if (!el) return;

        el.classList.add("translate-y-full");

        var event = new CustomEvent("ls:stickybar:hidden", { detail: { id: targetId } });
        document.dispatchEvent(event);
    }

    window.LoadShareStickyBar = {
        show: showStickyBar,
        hide: hideStickyBar
    };

    // Global alias for existing template onclick bindings
    window.dismissBottomBar = function () {
        hideStickyBar("stickyBottomBar");
    };
})();
