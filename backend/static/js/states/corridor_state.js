/**
 * corridor_state.js: Client-side interactive controller for the Corridor Search & Booking View.
 *
 * Provides:
 * - 3-step progressive booking wizard navigation (Pickup/Drop -> Departure -> Weight).
 * - Live truck selection and pinned bottom reservation action bar.
 * - Reviewer test state switcher (Default, Loading Skeleton, Empty, Capacity, Error).
 */
(function (window, document) {
    "use strict";

    var currentStep = 1;

    /**
     * Navigate between 3 wizard steps.
     * @param {number} step - Target step (1, 2, or 3).
     */
    function goToWizardStep(step) {
        currentStep = step;
        if (window.CarouselComponent && window.CarouselComponent.goToStep) {
            window.CarouselComponent.goToStep("search-engine", step);
        }
    }

    /**
     * Highlight selected departure window button.
     * @param {HTMLElement} btn
     */
    function selectDateWindow(btn) {
        var buttons = document.querySelectorAll(".date-pill");
        buttons.forEach(function (b) {
            b.classList.remove("active", "bg-primary", "text-on-primary", "border-primary", "shadow-xs");
            b.classList.add("bg-surface-container-lowest", "text-primary", "border-outline-variant");
        });
        if (btn) {
            btn.classList.remove("bg-surface-container-lowest", "text-primary", "border-outline-variant");
            btn.classList.add("active", "bg-primary", "text-on-primary", "border-primary", "shadow-xs");
        }
    }

    /**
     * Highlight selected consignment weight slab button.
     * @param {string} slab
     * @param {HTMLElement} btn
     */
    function selectWeightSlab(slab, btn) {
        var buttons = document.querySelectorAll(".weight-pill");
        buttons.forEach(function (b) {
            b.classList.remove("active", "border-secondary", "bg-secondary-fixed", "text-on-secondary-fixed", "shadow-xs");
            b.classList.add("border-outline-variant", "bg-surface-container-lowest", "text-primary");
        });
        if (btn) {
            btn.classList.remove("border-outline-variant", "bg-surface-container-lowest", "text-primary");
            btn.classList.add("active", "border-secondary", "bg-secondary-fixed", "text-on-secondary-fixed", "shadow-xs");
        }
    }

    /**
     * Trigger simulated truck search with skeleton transition.
     */
    function triggerSearch() {
        setCorridorState("skeleton");
        window.setTimeout(function () {
            setCorridorState("default");
            var resultsEl = document.getElementById("results-container");
            if (resultsEl) {
                resultsEl.scrollIntoView({ behavior: "smooth" });
            }
        }, 400);
    }

    /**
     * Switch reviewer preview states.
     * @param {string} state - 'default' | 'skeleton' | 'empty' | 'capacity' | 'error'
     */
    function setCorridorState(state) {
        var def = document.getElementById("stateCardsDefault");
        var skel = document.getElementById("stateCardsSkeleton");
        var emp = document.getElementById("stateCardsEmpty");
        var cap = document.getElementById("stateCardsCapacity");
        var err = document.getElementById("stateCardsError");
        var head = document.getElementById("resultsHeader");

        var btnDef = document.getElementById("btnStateDefault");
        var btnSkel = document.getElementById("btnStateSkeleton");
        var btnEmp = document.getElementById("btnStateEmpty");
        var btnCap = document.getElementById("btnStateCapacity");
        var btnErr = document.getElementById("btnStateError");

        var states = [def, skel, emp, cap, err];
        states.forEach(function (el) {
            if (el) el.classList.add("hidden");
        });

        var buttons = [btnDef, btnSkel, btnEmp, btnCap, btnErr];
        buttons.forEach(function (b) {
            if (b) {
                b.className = "px-2 py-0.5 rounded text-[11px] font-bold bg-surface-container-lowest border border-outline-variant hover:bg-surface-container text-primary transition-all";
            }
        });

        var activeBtnClass = "px-2 py-0.5 rounded text-[11px] font-bold bg-primary text-on-primary transition-all";

        if (state === "default") {
            if (def) def.classList.remove("hidden");
            if (head) head.classList.remove("hidden");
            if (btnDef) btnDef.className = activeBtnClass;
        } else if (state === "skeleton") {
            if (skel) skel.classList.remove("hidden");
            if (head) head.classList.remove("hidden");
            if (btnSkel) btnSkel.className = activeBtnClass;
        } else if (state === "empty") {
            if (emp) emp.classList.remove("hidden");
            if (head) head.classList.add("hidden");
            if (btnEmp) btnEmp.className = activeBtnClass;
        } else if (state === "capacity") {
            if (cap) cap.classList.remove("hidden");
            if (head) head.classList.add("hidden");
            if (btnCap) btnCap.className = activeBtnClass;
        } else if (state === "error") {
            if (err) err.classList.remove("hidden");
            if (head) head.classList.add("hidden");
            if (btnErr) btnErr.className = activeBtnClass;
        }
    }

    /**
     * Select a linehaul truck and show the pinned bottom reserve bar.
     * @param {string} time
     * @param {string} type
     * @param {string} price
     * @param {HTMLElement} btn
     */
    function selectTruck(time, type, price, btn) {
        var bar = document.getElementById("stickyBottomBar");
        var summary = document.getElementById("pinnedTruckSummary");
        if (summary) {
            summary.textContent = time + " departure · " + type + " · " + price;
        }
        if (bar) {
            bar.classList.remove("translate-y-full");
        }

        var buttons = document.querySelectorAll(".select-truck-btn");
        buttons.forEach(function (b) {
            b.className = "select-truck-btn bg-surface-container hover:bg-secondary hover:text-on-secondary text-primary px-3.5 py-1.5 rounded-lg text-xs font-bold font-mono transition-all";
        });
        if (btn) {
            btn.className = "select-truck-btn bg-secondary text-on-secondary px-3.5 py-1.5 rounded-lg text-xs font-bold font-mono transition-all shadow-xs";
        }
    }

    /**
     * Dismiss pinned truck selection bar.
     */
    function dismissBottomBar() {
        var bar = document.getElementById("stickyBottomBar");
        if (bar) {
            bar.classList.add("translate-y-full");
        }
    }

    /**
     * Confirm reserve action.
     */
    function confirmBooking() {
        window.alert("Opening LoadShare OTP Booking:\nLinehaul space reserved on NH48. Driver SMS verification code will be dispatched to your phone.");
    }

    /**
     * Update drop hub label from dropdown.
     * @param {string} val
     */
    function updateDropHub(val) {
        var el = document.getElementById("displayDropHub");
        if (el) el.textContent = val;
    }

    /**
     * Quick pickup selection visual feedback.
     * @param {string} name
     * @param {HTMLElement} btn
     */
    function quickSelectPickup(name, btn) {
        if (btn) {
            btn.classList.add("border-secondary", "bg-surface-container");
            window.setTimeout(function () {
                btn.classList.remove("border-secondary", "bg-surface-container");
            }, 300);
        }
    }

    /**
     * Location click feedback.
     * @param {HTMLElement} btn
     */
    function simulateLocationClick(btn) {
        if (btn) {
            btn.classList.add("opacity-75");
            window.setTimeout(function () {
                btn.classList.remove("opacity-75");
            }, 500);
        }
    }

    // Public API
    window.LoadShareCorridor = {
        goToStep: goToWizardStep,
        selectDateWindow: selectDateWindow,
        selectWeightSlab: selectWeightSlab,
        triggerSearch: triggerSearch,
        setCorridorState: setCorridorState,
        selectTruck: selectTruck,
        dismissBottomBar: dismissBottomBar,
        confirmBooking: confirmBooking,
        updateDropHub: updateDropHub,
        quickSelectPickup: quickSelectPickup,
        simulateLocationClick: simulateLocationClick
    };

    // Global aliases for clean template callbacks
    window.goToWizardStep = goToWizardStep;
    window.selectDateWindow = selectDateWindow;
    window.selectWeightSlab = selectWeightSlab;
    window.triggerSearch = triggerSearch;
    window.setTestState = setCorridorState;
    window.selectTruck = selectTruck;
    window.dismissBottomBar = dismissBottomBar;
    window.confirmBooking = confirmBooking;
    window.updateDropHub = updateDropHub;
    window.quickSelectPickup = quickSelectPickup;
    window.simulateLocationClick = simulateLocationClick;

})(window, document);
