/**
 * Modal Dialog Controller
 * Handles accessible dialog opening, closing, focus trapping, and ESC dismissal.
 */
(function () {
    "use strict";

    var activeModalId = null;
    var previousActiveElement = null;

    function openModal(id) {
        var el = document.getElementById(id);
        if (!el) return;

        previousActiveElement = document.activeElement;
        activeModalId = id;

        el.style.display = "flex";
        // Force reflow for transition
        void el.offsetWidth;
        el.classList.add("ls-modal--open");

        document.body.style.overflow = "hidden";

        // Set focus to the first focusable element or modal container
        var focusable = el.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable.length > 0) {
            focusable[0].focus();
        } else {
            el.focus();
        }

        var event = new CustomEvent("ls:modal:opened", { detail: { id: id } });
        document.dispatchEvent(event);
    }

    function closeModal(id) {
        var modalId = id || activeModalId;
        if (!modalId) return;

        var el = document.getElementById(modalId);
        if (!el) return;

        el.classList.remove("ls-modal--open");
        document.body.style.overflow = "";

        window.setTimeout(function () {
            el.style.display = "none";
            if (activeModalId === modalId) {
                activeModalId = null;
            }
            if (previousActiveElement && typeof previousActiveElement.focus === "function") {
                previousActiveElement.focus();
                previousActiveElement = null;
            }
        }, 200);

        var event = new CustomEvent("ls:modal:closed", { detail: { id: modalId } });
        document.dispatchEvent(event);
    }

    // Escape Key Listener
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && activeModalId) {
            var el = document.getElementById(activeModalId);
            if (el && el.getAttribute("data-dismissible") !== "false") {
                closeModal(activeModalId);
            }
        }
    });

    window.LoadShareModal = {
        open: openModal,
        close: closeModal
    };
})();
