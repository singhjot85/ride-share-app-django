/**
 * profile_state.js: Client-side interactive controller for the Sender Profile View.
 *
 * Provides:
 * - Account details inline edit toggling (Business Name & Phone).
 * - Bookings list tab filtering (All, Active, Completed).
 * - Empty state simulation demo switcher.
 * - Sign out confirmation and redirection.
 */
(function (window, document) {
    "use strict";

    var currentFilter = "all";
    var isForcedEmpty = false;

    /**
     * Toggle between account display mode and edit mode.
     * @param {boolean} isEdit
     */
    function toggleProfileEdit(isEdit) {
        var viewMode = document.getElementById("account-view-mode");
        var editMode = document.getElementById("account-edit-mode");
        var inputName = document.getElementById("input-name");

        if (viewMode && editMode) {
            if (isEdit) {
                viewMode.classList.add("hidden");
                editMode.classList.remove("hidden");
                if (inputName) inputName.focus();
            } else {
                editMode.classList.add("hidden");
                viewMode.classList.remove("hidden");
            }
        }
    }

    /**
     * Handle account details form submission.
     * @param {Event} event
     */
    function saveProfile(event) {
        if (event && event.preventDefault) {
            event.preventDefault();
        }

        var inputName = document.getElementById("input-name");
        var inputPhone = document.getElementById("input-phone");
        var displayName = document.getElementById("display-name");
        var displayPhone = document.getElementById("display-phone");

        if (inputName && displayName && inputName.value.trim()) {
            displayName.textContent = inputName.value.trim();
        }
        if (inputPhone && displayPhone && inputPhone.value.trim()) {
            displayPhone.textContent = inputPhone.value.trim();
        }

        toggleProfileEdit(false);
    }

    /**
     * Filter bookings cards list by status.
     * @param {string} filter - 'all' | 'active' | 'completed'
     */
    function setBookingFilter(filter) {
        currentFilter = filter;
        var filterAll = document.getElementById("filter-all");
        var filterActive = document.getElementById("filter-active");
        var filterCompleted = document.getElementById("filter-completed");

        var chips = {
            all: filterAll,
            active: filterActive,
            completed: filterCompleted
        };

        var activeChipClass = "booking-filter-chip bg-primary text-on-primary font-bold text-xs px-3.5 py-1.5 rounded-full transition-all shrink-0 shadow-xs";
        var inactiveChipClass = "booking-filter-chip bg-surface-container-low text-on-surface-variant font-semibold text-xs px-3.5 py-1.5 rounded-full hover:bg-surface-container transition-all shrink-0";

        Object.keys(chips).forEach(function (key) {
            var chip = chips[key];
            if (chip) {
                chip.className = (key === filter) ? activeChipClass : inactiveChipClass;
            }
        });

        if (isForcedEmpty) return;

        var items = document.querySelectorAll(".booking-item");
        var visibleCount = 0;

        items.forEach(function (item) {
            var status = item.getAttribute("data-status");
            if (filter === "all" || status === filter) {
                item.style.display = "";
                visibleCount++;
            } else {
                item.style.display = "none";
            }
        });

        var countBadge = document.getElementById("booking-count-badge");
        if (countBadge) {
            countBadge.textContent = visibleCount;
        }
    }

    /**
     * Toggle between simulated empty state and populated bookings list.
     */
    function toggleEmptyState() {
        isForcedEmpty = !isForcedEmpty;
        var cardsList = document.getElementById("booking-cards-list");
        var emptyState = document.getElementById("booking-empty-state");
        var toggleBtn = document.getElementById("toggle-empty-state-btn");
        var countBadge = document.getElementById("booking-count-badge");

        if (isForcedEmpty) {
            if (cardsList) cardsList.classList.add("hidden");
            if (emptyState) {
                emptyState.classList.remove("hidden");
                emptyState.classList.add("flex");
            }
            if (countBadge) countBadge.textContent = "0";
            if (toggleBtn) {
                var restoreText = toggleBtn.getAttribute("data-restore-text") || "Restore list";
                toggleBtn.textContent = restoreText;
            }
        } else {
            if (cardsList) cardsList.classList.remove("hidden");
            if (emptyState) {
                emptyState.classList.add("hidden");
                emptyState.classList.remove("flex");
            }
            if (toggleBtn) {
                var simText = toggleBtn.getAttribute("data-sim-text") || "Simulate empty";
                toggleBtn.textContent = simText;
            }
            setBookingFilter(currentFilter);
        }
    }

    /**
     * Sign out user confirmation dialog.
     */
    function confirmSignOut() {
        var msg = "Are you sure you want to sign out of LoadShare?";
        if (window.confirm(msg)) {
            // Delete cookies & route to login
            document.cookie = "loadshare_jwt=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            document.cookie = "access_token=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            window.location.href = "/login/";
        }
    }

    // Public API
    window.LoadShareProfile = {
        toggleEdit: toggleProfileEdit,
        saveProfile: saveProfile,
        setFilter: setBookingFilter,
        toggleEmptyState: toggleEmptyState,
        confirmSignOut: confirmSignOut
    };

    // Global aliases for clean template callbacks
    window.toggleProfileEdit = toggleProfileEdit;
    window.saveProfile = saveProfile;
    window.setFilter = setBookingFilter;
    window.setBookingFilter = setBookingFilter;
    window.toggleEmptyState = toggleEmptyState;
    window.confirmSignOut = confirmSignOut;

})(window, document);
