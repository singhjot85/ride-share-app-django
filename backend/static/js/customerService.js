/**
 * customerService.js: API client and profile coordinator for Customer domain.
 *
 * Capabilities:
 * - Fetch authenticated customer data from CRM endpoint: /api/customers/v1/customers/{id}/.
 * - Extract customer name (business/full), primary phone, and primary email.
 * - Populate profile view DOM elements and inline edit form.
 * - Derive language preference from customer preferences and synchronize site language.
 * - Handle customer profile updates via CRM PUT endpoint.
 * - Orchestrate onLoginSuccess workflow upon authentication.
 */
(function (window, document) {
    "use strict";

    var CRM_CUSTOMERS_BASE = "/api/customers/v1/customers/";

    /**
     * Parse named cookie from document.cookie.
     * @param {string} name
     * @returns {string|null}
     */
    function getCookie(name) {
        var match = document.cookie.match(new RegExp("(?:^|;\\s*)" + name + "=([^;]*)"));
        return match ? decodeURIComponent(match[1]) : null;
    }

    /**
     * Get active CSRF token.
     * @returns {string}
     */
    function getCSRFToken() {
        if (window.Core && typeof window.Core.getCSRFToken === "function") {
            return window.Core.getCSRFToken();
        }
        return getCookie("csrftoken") || "";
    }

    /**
     * Build standard authenticated HTTP headers.
     * @returns {Object}
     */
    function getAuthHeaders() {
        var headers = {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        };
        var token = getCookie("access_token") || getCookie("loadshare_jwt");
        if (token) {
            headers["Authorization"] = "Bearer " + token;
        }
        return headers;
    }

    /**
     * Resolve the active customer ID from the DOM, cookies, window, or session.
     * @returns {string|null}
     */
    function getCustomerId() {
        // 1. From profile view container data attribute
        var profileView = document.getElementById("view-profile");
        if (profileView && profileView.dataset.customerId) {
            return profileView.dataset.customerId;
        }
        // 2. From page meta tag
        var metaTag = document.querySelector('meta[name="customer-id"]');
        if (metaTag && metaTag.getAttribute("content")) {
            return metaTag.getAttribute("content");
        }
        // 3. From global window variable
        if (window.LOADSHARE_CUSTOMER_ID) {
            return window.LOADSHARE_CUSTOMER_ID;
        }
        // 4. From customer_id cookie
        var cookieVal = getCookie("customer_id");
        if (cookieVal) {
            return cookieVal;
        }
        // 5. From sessionStorage cache
        try {
            var stored = sessionStorage.getItem("customer_id");
            if (stored) return stored;
        } catch (e) {}

        return null;
    }

    /**
     * Fetch customer profile details from CRM retrieve endpoint:
     * GET /api/customers/v1/customers/{customer_id}/
     * @param {string} [customerId] - Optional explicit customer ID.
     * @returns {Promise<Object|null>}
     */
    async function fetchCustomerData(customerId) {
        var id = customerId || getCustomerId();
        if (!id) {
            return null;
        }
        try {
            var url = CRM_CUSTOMERS_BASE + encodeURIComponent(id) + "/";
            var response = await fetch(url, {
                method: "GET",
                headers: getAuthHeaders(),
                credentials: "same-origin"
            });
            if (!response.ok) {
                if (response.status === 401 || response.status === 403 || response.status === 404) {
                    return null;
                }
                throw new Error("CRM Customer API error: HTTP " + response.status);
            }
            var data = await response.json();
            // Cache customer ID in sessionStorage for fast lookup
            try {
                if (data && data.id) {
                    sessionStorage.setItem("customer_id", data.id);
                }
            } catch (e) {}
            return data;
        } catch (error) {
            console.debug("CustomerService: Error fetching customer data:", error);
            return null;
        }
    }

    /**
     * Extract primary phone number from customer profile.
     * @param {Object} customer
     * @returns {string}
     */
    function extractPhone(customer) {
        if (!customer) return "";
        if (customer.phones && customer.phones.length > 0) {
            var primary = customer.phones.find(function (p) { return p.is_primary; });
            return (primary || customer.phones[0]).phone || "";
        }
        return customer.phone_number || "";
    }

    /**
     * Extract primary email address from customer profile.
     * @param {Object} customer
     * @returns {string}
     */
    function extractEmail(customer) {
        if (!customer) return "";
        if (customer.emails && customer.emails.length > 0) {
            var primary = customer.emails.find(function (e) { return e.is_primary; });
            return (primary || customer.emails[0]).email || "";
        }
        return customer.email || "";
    }

    /**
     * Extract customer display name (business name, full name, or first/last).
     * @param {Object} customer
     * @returns {string}
     */
    function extractName(customer) {
        if (!customer) return "";
        if (customer.business_name && customer.business_name.trim()) {
            return customer.business_name.trim();
        }
        if (customer.full_name && customer.full_name.trim()) {
            return customer.full_name.trim();
        }
        var parts = [customer.first_name, customer.last_name].filter(Boolean);
        if (parts.length > 0) {
            return parts.join(" ").trim();
        }
        return customer.username || "";
    }

    /**
     * Derive language preference code from customer preferences list.
     * @param {Object} customer
     * @returns {string|null}
     */
    function deriveLanguagePreference(customer) {
        if (!customer || !customer.preferences || !Array.isArray(customer.preferences)) {
            return null;
        }
        var langPref = customer.preferences.find(function (p) {
            return p.preference_code === "language" ||
                   p.preference_code === "lang" ||
                   (p.preference_type && p.preference_type.code === "language");
        });
        if (langPref && langPref.value) {
            var val = typeof langPref.value === "string" ? langPref.value.toLowerCase() : String(langPref.value);
            return (val === "hi" || val === "en") ? val : null;
        }
        return null;
    }

    /**
     * Synchronize site language using active window language toggle handler.
     * @param {string} lang - 'en' | 'hi'
     */
    function applySiteLanguage(lang) {
        if (!lang) return;
        if (typeof window.setLanguage === "function") {
            var current = typeof window.getActiveLanguage === "function" ? window.getActiveLanguage() : null;
            if (current !== lang) {
                window.setLanguage(lang);
            }
        }
    }

    /**
     * Populate profile view DOM elements with customer data.
     * @param {Object} customer
     */
    function populateProfile(customer) {
        if (!customer) return;

        var name = extractName(customer);
        var phone = extractPhone(customer);
        var email = extractEmail(customer);

        var displayName = document.getElementById("display-name");
        var displayPhone = document.getElementById("display-phone");
        var displayEmail = document.getElementById("display-email");
        var emailContainer = document.getElementById("email-container");
        var inputName = document.getElementById("input-name");
        var inputPhone = document.getElementById("input-phone");
        var inputEmail = document.getElementById("input-email");

        if (displayName && name) displayName.textContent = name;
        if (displayPhone && phone) displayPhone.textContent = phone;
        if (displayEmail) {
            displayEmail.textContent = email || "—";
            if (emailContainer && !email) {
                emailContainer.style.display = "none";
            } else if (emailContainer) {
                emailContainer.style.display = "";
            }
        }

        if (inputName && name) inputName.value = name;
        if (inputPhone && phone) inputPhone.value = phone;
        if (inputEmail && email) inputEmail.value = email;
    }

    /**
     * Update customer profile via CRM PUT endpoint:
     * PUT /api/customers/v1/customers/{customer_id}/
     * @param {Object} data - { business_name, first_name, last_name, ... }
     * @param {string} [customerId] - Optional explicit customer ID.
     * @returns {Promise<Object>}
     */
    async function updateCustomer(data, customerId) {
        var id = customerId || getCustomerId();
        if (!id) {
            throw new Error("No customer ID available for update.");
        }
        try {
            var url = CRM_CUSTOMERS_BASE + encodeURIComponent(id) + "/";
            var payload = {
                customer_type: data.customer_type || "individual"
            };
            if (data.business_name) {
                payload.business_name = data.business_name;
            } else if (data.name) {
                payload.business_name = data.name;
            } else {
                if (data.first_name) payload.first_name = data.first_name;
                if (data.last_name) payload.last_name = data.last_name;
            }

            var response = await fetch(url, {
                method: "PUT",
                headers: getAuthHeaders(),
                credentials: "same-origin",
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                throw new Error("Failed to update customer: HTTP " + response.status);
            }

            // Retrieve updated customer representation with embedded relations
            var updated = await fetchCustomerData(id);
            if (updated) {
                populateProfile(updated);
                var lang = deriveLanguagePreference(updated);
                if (lang) {
                    applySiteLanguage(lang);
                }
            }
            return updated || await response.json();
        } catch (error) {
            console.error("CustomerService: Update error:", error);
            throw error;
        }
    }

    /**
     * Complete lifecycle flow triggered on successful login or authenticated page load:
     * 1. Resolve customer ID and fetch customer data via CRM retrieve endpoint.
     * 2. Populate customer phone, email, and customer name into the DOM.
     * 3. Derive language preference from preferences and apply to site language.
     * @param {string} [customerId] - Optional customer ID.
     * @returns {Promise<Object|null>}
     */
    async function onLoginSuccess(customerId) {
        var customer = await fetchCustomerData(customerId);
        if (customer) {
            populateProfile(customer);
            var lang = deriveLanguagePreference(customer);
            if (lang) {
                applySiteLanguage(lang);
            }
        }
        return customer;
    }

    // Public API on global window
    window.CustomerService = {
        getCustomerId: getCustomerId,
        fetchCustomerData: fetchCustomerData,
        extractPhone: extractPhone,
        extractEmail: extractEmail,
        extractName: extractName,
        deriveLanguagePreference: deriveLanguagePreference,
        applySiteLanguage: applySiteLanguage,
        populateProfile: populateProfile,
        updateCustomer: updateCustomer,
        onLoginSuccess: onLoginSuccess
    };

    // Auto-init on authenticated surfaces
    document.addEventListener("DOMContentLoaded", function () {
        var profileView = document.getElementById("view-profile");
        var accountCard = document.getElementById("account-card");
        if (profileView || accountCard) {
            onLoginSuccess();
        }
    });

})(window, document);
