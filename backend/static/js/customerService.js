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
     * Choices mapping adhering to CRM ContactTypeChoices and AddressTypeChoices.
     */
    var CONTACT_TYPE_CHOICES = {
        work: "Work",
        personal: "Personal",
        other: "Other"
    };

    var ADDRESS_TYPE_CHOICES = {
        permanent: "Permanent",
        current: "Current",
        billing: "Billing",
        shipping: "Shipping",
        office: "Office",
        work: "Work",
        other: "Other"
    };

    /**
     * Extract primary address from customer profile.
     * @param {Object} customer
     * @returns {string}
     */
    function extractPrimaryAddress(customer) {
        if (!customer || !customer.addresses || customer.addresses.length === 0) {
            return "";
        }
        var primary = customer.addresses.find(function (a) { return a.is_primary; });
        var addr = primary || customer.addresses[0];
        if (addr.full_address) return addr.full_address;
        var parts = [addr.address_line_1, addr.address_line_2, addr.city, addr.state, addr.postal_code].filter(Boolean);
        return parts.join(", ");
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
        var address = extractPrimaryAddress(customer);

        var displayName = document.getElementById("display-name");
        var displayPhone = document.getElementById("display-phone");
        var displayEmail = document.getElementById("display-email");
        var displayAddress = document.getElementById("display-address");
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
        if (displayAddress && address) {
            displayAddress.textContent = address;
            displayAddress.setAttribute("title", address);
        }

        if (inputName && name) inputName.value = name;
        if (inputPhone && phone) inputPhone.value = phone;
        if (inputEmail && email) inputEmail.value = email;

        // 1. Verified Badge vs Progress Bar
        var verifiedBadge = document.getElementById("customer-verified-badge");
        var progressContainer = document.getElementById("customer-verification-progress-container");
        var isVerified = Boolean(customer.is_verified);

        if (isVerified) {
            if (verifiedBadge) verifiedBadge.classList.remove("hidden");
            if (progressContainer) progressContainer.classList.add("hidden");
        } else {
            if (verifiedBadge) verifiedBadge.classList.add("hidden");
            if (progressContainer) progressContainer.classList.remove("hidden");

            // Calculate verification progress from contacts & identity
            var hasVerifiedPhone = (customer.phones && customer.phones.some(function (p) { return p.is_verified; })) || Boolean(phone);
            var hasVerifiedEmail = Boolean(customer.emails && customer.emails.some(function (e) { return e.is_verified; }));
            var hasAddress = Boolean(customer.addresses && customer.addresses.length > 0);
            var hasVerifiedId = Boolean(customer.identifications && customer.identifications.some(function (i) { return i.is_verified; }));

            var steps = (hasVerifiedPhone ? 1 : 0) + (hasVerifiedEmail ? 1 : 0) + (hasAddress ? 1 : 0) + (hasVerifiedId ? 1 : 0);
            var pct = steps * 25;

            var progressText = document.getElementById("verification-progress-text");
            var progressBar = document.getElementById("verification-progress-bar");
            if (progressText) progressText.textContent = pct + "%";
            if (progressBar) progressBar.style.width = pct + "%";
        }

        // 2. Member since (rendered only if customer.created is present)
        var memberSinceElem = document.getElementById("customer-member-since");
        var memberSinceText = document.getElementById("customer-member-since-text");
        if (customer.created) {
            var d = new Date(customer.created);
            var formatted = !isNaN(d.getTime()) ? d.toLocaleDateString("en-US", { month: "short", year: "numeric" }) : customer.created;
            var isHi = (window.getActiveLanguage && window.getActiveLanguage() === "hi");
            var label = (isHi ? "सदस्यता " : "Member since ") + formatted;
            if (memberSinceText) memberSinceText.textContent = label;
            if (memberSinceElem) memberSinceElem.classList.remove("hidden");
        }

        // 3. Maximized Details: Phones, Emails, Addresses, Identifications
        populateMaximizedDetails(customer);
    }

    /**
     * Populate lists inside the maximized customer profile details panel.
     * @param {Object} customer
     */
    function populateMaximizedDetails(customer) {
        if (!customer) return;

        // Phones List
        var phonesList = document.getElementById("customer-phones-list");
        var phonesCount = document.getElementById("phones-count");
        if (phonesList && customer.phones && customer.phones.length > 0) {
            phonesList.innerHTML = "";
            customer.phones.forEach(function (p) {
                var item = document.createElement("div");
                item.className = "flex items-center gap-2 text-xs";
                var typeLabel = CONTACT_TYPE_CHOICES[p.phone_type] || p.phone_type || "Contact";
                var badgeClass = p.is_primary
                    ? "min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-primary bg-primary px-2 py-1 rounded text-center flex-shrink-0 shadow-xs ring-1 ring-primary/30 whitespace-nowrap"
                    : "min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-surface-variant bg-surface-container px-2 py-1 rounded text-center flex-shrink-0 whitespace-nowrap";
                var verifiedBadge = p.is_verified ?
                    '<span class="inline-flex items-center text-emerald-600 dark:text-emerald-400" title="Verified"><span class="material-symbols-outlined text-[15px]" aria-hidden="true">verified</span></span>' :
                    '<span class="inline-flex items-center text-amber-500/90 dark:text-amber-400/90" title="Unverified"><span class="material-symbols-outlined text-[15px]" aria-hidden="true">pending</span></span>';

                item.innerHTML = '<span class="' + badgeClass + '" title="' + escapeHtml(typeLabel) + '">' + escapeHtml(typeLabel) + '</span>' +
                    '<div class="flex-1 flex items-center justify-between p-2 rounded-lg bg-surface-container/30 border border-outline-variant/30">' +
                    '<span class="font-mono font-medium text-primary">' + escapeHtml(p.phone) + '</span>' +
                    verifiedBadge +
                    '</div>';
                phonesList.appendChild(item);
            });
            if (phonesCount) phonesCount.textContent = String(customer.phones.length);
        }

        // Emails List
        var emailsList = document.getElementById("customer-emails-list");
        var emailsCount = document.getElementById("emails-count");
        if (emailsList && customer.emails && customer.emails.length > 0) {
            emailsList.innerHTML = "";
            customer.emails.forEach(function (e) {
                var item = document.createElement("div");
                item.className = "flex items-center gap-2 text-xs";
                var typeLabel = CONTACT_TYPE_CHOICES[e.email_type] || e.email_type || "Email";
                var badgeClass = e.is_primary
                    ? "min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-primary bg-primary px-2 py-1 rounded text-center flex-shrink-0 shadow-xs ring-1 ring-primary/30 whitespace-nowrap"
                    : "min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-surface-variant bg-surface-container px-2 py-1 rounded text-center flex-shrink-0 whitespace-nowrap";
                var verifiedBadge = e.is_verified ?
                    '<span class="inline-flex items-center text-emerald-600 dark:text-emerald-400 flex-shrink-0" title="Verified"><span class="material-symbols-outlined text-[15px]" aria-hidden="true">verified</span></span>' :
                    '<span class="inline-flex items-center text-amber-500/90 dark:text-amber-400/90 flex-shrink-0" title="Unverified"><span class="material-symbols-outlined text-[15px]" aria-hidden="true">pending</span></span>';

                item.innerHTML = '<span class="' + badgeClass + '" title="' + escapeHtml(typeLabel) + '">' + escapeHtml(typeLabel) + '</span>' +
                    '<div class="flex-1 flex items-center justify-between p-2 rounded-lg bg-surface-container/30 border border-outline-variant/30">' +
                    '<span class="font-mono font-medium text-primary truncate">' + escapeHtml(e.email) + '</span>' +
                    verifiedBadge +
                    '</div>';
                emailsList.appendChild(item);
            });
            if (emailsCount) emailsCount.textContent = String(customer.emails.length);
        }

        // Addresses List
        var addressesList = document.getElementById("customer-addresses-list");
        var addressesCount = document.getElementById("addresses-count");
        if (addressesList && customer.addresses && customer.addresses.length > 0) {
            addressesList.innerHTML = "";
            customer.addresses.forEach(function (a) {
                var item = document.createElement("div");
                item.className = "flex items-start gap-2 text-xs";
                var typeLabel = ADDRESS_TYPE_CHOICES[a.address_type] || a.address_type || "Address";
                var badgeClass = a.is_primary
                    ? "min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-primary bg-primary px-2 py-1 rounded text-center flex-shrink-0 mt-0.5 shadow-xs ring-1 ring-primary/30 whitespace-nowrap"
                    : "min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-surface-variant bg-surface-container px-2 py-1 rounded text-center flex-shrink-0 mt-0.5 whitespace-nowrap";
                var fullAddr = a.full_address || [a.address_line_1, a.address_line_2, a.city, a.state, a.postal_code].filter(Boolean).join(", ");

                item.innerHTML = '<span class="' + badgeClass + '" title="' + escapeHtml(typeLabel) + '">' + escapeHtml(typeLabel) + '</span>' +
                    '<div class="flex-1 p-2.5 rounded-lg bg-surface-container/30 border border-outline-variant/30">' +
                    '<p class="text-primary font-medium leading-snug">' + escapeHtml(fullAddr) + '</p>' +
                    '</div>';
                addressesList.appendChild(item);
            });
            if (addressesCount) addressesCount.textContent = String(customer.addresses.length);
        }

        // Identifications List
        var idList = document.getElementById("customer-identifications-list");
        var idCount = document.getElementById("identifications-count");
        if (idList && customer.identifications && customer.identifications.length > 0) {
            idList.innerHTML = "";
            customer.identifications.forEach(function (i) {
                var item = document.createElement("div");
                item.className = "flex items-center gap-2 text-xs";
                var typeLabel = i.identity_type_display || i.type || "Document";
                var verifiedBadge = i.is_verified ?
                    '<span class="inline-flex items-center text-emerald-600 dark:text-emerald-400" title="Verified"><span class="material-symbols-outlined text-[15px]" aria-hidden="true">verified</span></span>' :
                    '<span class="inline-flex items-center text-amber-500/90 dark:text-amber-400/90" title="' + escapeHtml(i.status || "Pending") + '"><span class="material-symbols-outlined text-[15px]" aria-hidden="true">pending</span></span>';

                var docAction = "";
                if (i.document) {
                    docAction = '<a href="' + escapeHtml(i.document) + '" download target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-surface-container hover:bg-surface-container-high text-primary font-semibold text-[11px] border border-outline-variant/40 transition-colors shadow-xs active:scale-95" title="Download Document">' +
                        '<span class="material-symbols-outlined text-[14px]" aria-hidden="true">download</span>' +
                        '<span>Download</span></a>';
                } else {
                    docAction = '<span class="text-on-surface-variant text-[11px] italic">No file attached</span>';
                }

                item.innerHTML = '<span class="min-w-[4.5rem] sm:min-w-[5.5rem] text-[10px] uppercase font-mono font-bold text-on-surface-variant bg-surface-container px-2 py-1 rounded text-center flex-shrink-0 whitespace-nowrap" title="' + escapeHtml(typeLabel) + '">' + escapeHtml(typeLabel) + '</span>' +
                    '<div class="flex-1 flex items-center justify-between p-2 rounded-lg bg-surface-container/30 border border-outline-variant/30 gap-2">' +
                    '<div class="flex items-center gap-2 min-w-0">' + docAction + '</div>' +
                    '<div class="flex-shrink-0">' + verifiedBadge + '</div>' +
                    '</div>';
                idList.appendChild(item);
            });
            if (idCount) idCount.textContent = String(customer.identifications.length);
        }
    }

    /**
     * Minimal HTML entity escape utility.
     * @param {string} str
     * @returns {string}
     */
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
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
