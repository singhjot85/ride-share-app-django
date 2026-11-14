/**
 * profile_state.js: Client-side interactive controller for the Sender Profile View.
 *
 * Provides:
 * - Account details inline edit toggling (Name, Phone & Email).
 * - Live Customer profile update submission via CustomerService.
 * - Bookings list tab filtering (All, Active, Completed).
 * - Sign out confirmation and redirection.
 */
(function (window, document) {
    "use strict";

    var currentFilter = "all";
    var isForcedEmpty = true;

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
     * Toggle maximize/minimize customer full details panel.
     * @param {boolean} [forceState]
     */
    function toggleProfileMaximize(forceState) {
        var detailsPanel = document.getElementById("account-maximize-details");
        var toggleBtn = document.getElementById("toggle-maximize-btn");
        var maxIcon = document.getElementById("maximize-icon");
        var btnText = document.getElementById("maximize-btn-text");

        if (!detailsPanel) return;

        var isHidden = detailsPanel.classList.contains("hidden");
        var shouldShow = typeof forceState === "boolean" ? forceState : isHidden;

        if (shouldShow) {
            detailsPanel.classList.remove("hidden");
            if (toggleBtn) toggleBtn.setAttribute("aria-expanded", "true");
            if (maxIcon) maxIcon.classList.add("rotate-180");
            if (btnText) {
                var hideText = (window.getActiveLanguage && window.getActiveLanguage() === "hi") ? "विवरण छिपाएं" : "Hide details";
                btnText.textContent = hideText;
            }
        } else {
            detailsPanel.classList.add("hidden");
            if (toggleBtn) toggleBtn.setAttribute("aria-expanded", "false");
            if (maxIcon) maxIcon.classList.remove("rotate-180");
            if (btnText) {
                var showText = (window.getActiveLanguage && window.getActiveLanguage() === "hi") ? "सभी विवरण देखें" : "View all details";
                btnText.textContent = showText;
            }
        }
    }

    /**
     * Handle account details form submission and persist via CustomerService.
     * @param {Event} event
     */
    async function saveProfile(event) {
        if (event && event.preventDefault) {
            event.preventDefault();
        }

        var inputName = document.getElementById("input-name");
        var inputPhone = document.getElementById("input-phone");
        var inputEmail = document.getElementById("input-email");
        var displayName = document.getElementById("display-name");
        var displayPhone = document.getElementById("display-phone");
        var displayEmail = document.getElementById("display-email");
        var emailContainer = document.getElementById("email-container");

        var nameVal = inputName ? inputName.value.trim() : "";
        var phoneVal = inputPhone ? inputPhone.value.trim() : "";
        var emailVal = inputEmail ? inputEmail.value.trim() : "";

        if (nameVal && displayName) displayName.textContent = nameVal;
        if (phoneVal && displayPhone) displayPhone.textContent = phoneVal;
        if (displayEmail) {
            displayEmail.textContent = emailVal || "—";
            if (emailContainer) {
                emailContainer.style.display = emailVal ? "" : "none";
            }
        }

        toggleProfileEdit(false);

        if (window.CustomerService && typeof window.CustomerService.updateCustomer === "function") {
            try {
                await window.CustomerService.updateCustomer({
                    business_name: nameVal,
                    phone: phoneVal,
                    email: emailVal
                });
            } catch (err) {
                console.debug("Customer profile persist error:", err);
            }
        }
    }

    /**
     * Filter bookings cards list by status.
     * @param {string} filter - 'all' | 'active' | 'completed'
     */
    function setBookingFilter(filter) {
        currentFilter = filter;
        if (window.FilterChipsComponent && window.FilterChipsComponent.setActive) {
            window.FilterChipsComponent.setActive("booking-filters", filter, false);
        } else {
            var filterAll = document.getElementById("filter-all");
            var filterActive = document.getElementById("filter-active");
            var filterCompleted = document.getElementById("filter-completed");
            [filterAll, filterActive, filterCompleted].forEach(function (chip) {
                if (chip) {
                    var isMatch = chip.getAttribute("data-value") === filter;
                    chip.classList.toggle("is-active", isMatch);
                    chip.setAttribute("aria-selected", isMatch ? "true" : "false");
                }
            });
        }

        if (isForcedEmpty) {
            var countBadgeEmpty = document.getElementById("booking-count-badge");
            if (countBadgeEmpty) countBadgeEmpty.textContent = "0";
            return;
        }

        var cardsList = document.getElementById("booking-cards-list");
        var emptyState = document.getElementById("booking-empty-state");
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

        if (visibleCount === 0) {
            if (cardsList) cardsList.classList.add("hidden");
            if (emptyState) {
                emptyState.classList.remove("hidden");
                emptyState.classList.add("flex");
            }
        } else {
            if (cardsList) cardsList.classList.remove("hidden");
            if (emptyState) {
                emptyState.classList.add("hidden");
                emptyState.classList.remove("flex");
            }
        }
    }

    /**
     * Toggle between empty state and populated bookings list.
     */
    function toggleEmptyState() {
        isForcedEmpty = !isForcedEmpty;
        var cardsList = document.getElementById("booking-cards-list");
        var emptyState = document.getElementById("booking-empty-state");
        var toggleBtn = document.getElementById("toggle-empty-state-btn");
        var countBadge = document.getElementById("booking-count-badge");
        var container = document.getElementById("booking-cards-container");

        if (isForcedEmpty) {
            if (cardsList) cardsList.classList.add("hidden");
            if (emptyState) {
                emptyState.classList.remove("hidden");
                emptyState.classList.add("flex");
            }
            if (container) container.setAttribute("data-active-state", "empty");
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
            if (container) container.setAttribute("data-active-state", "populated");
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
        if (window.LoadShareModal && document.getElementById("signout-confirm-modal")) {
            window.LoadShareModal.open("signout-confirm-modal");
        } else {
            var msg = (window.getActiveLanguage && window.getActiveLanguage() === "hi")
                ? "क्या आप वाकई लोडशेयर से साइन आउट करना चाहते हैं?"
                : "Are you sure you want to sign out of LoadShare?";
            if (window.confirm(msg)) {
                executeSignOut();
            }
        }
    }

    /**
     * Execute sign out and clear session tokens.
     */
    function executeSignOut() {
        var cookieNames = [
            "access_token",
            "refresh_token",
            "loadshare_jwt",
            "customer_id",
            "sessionid",
            "jwt_auth_synced"
        ];
        for (var i = 0; i < cookieNames.length; i++) {
            var name = cookieNames[i];
            document.cookie = name + "=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            document.cookie = name + "=; path=/; domain=" + window.location.hostname + "; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        }

        try {
            if (window.sessionStorage) {
                sessionStorage.removeItem("customer_id");
                sessionStorage.removeItem("customer_data");
                sessionStorage.removeItem("jwt_auth_synced");
                sessionStorage.clear();
            }
            if (window.localStorage) {
                localStorage.removeItem("customer_id");
                localStorage.removeItem("customer_data");
            }
        } catch (e) {
            console.debug("Sign out storage clear error:", e);
        }

        window.location.href = "/logout/";
    }

    // Public API
    window.LoadShareProfile = {
        toggleEdit: toggleProfileEdit,
        toggleMaximize: toggleProfileMaximize,
        saveProfile: saveProfile,
        setFilter: setBookingFilter,
        toggleEmptyState: toggleEmptyState,
        confirmSignOut: confirmSignOut,
        executeSignOut: executeSignOut
    };

    // Global aliases for clean template callbacks
    window.toggleProfileEdit = toggleProfileEdit;
    window.toggleProfileMaximize = toggleProfileMaximize;
    window.saveProfile = saveProfile;
    window.setFilter = setBookingFilter;
    window.setBookingFilter = setBookingFilter;
    window.toggleEmptyState = toggleEmptyState;
    window.confirmSignOut = confirmSignOut;
    window.executeSignOut = executeSignOut;

})(window, document);
