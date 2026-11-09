/**
 * otp_signup.js: OTP Login and Signup submission handlers with Customer API integration.
 */
document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // Switch to initial tab if requested via data attribute
    var container = document.getElementById("otp_auth_container");
    var initialTab = container ? container.dataset.initialTab : "login";
    if (initialTab === "signup" && window.Core && Core.auth && typeof Core.auth.switchOTPTab === "function") {
        Core.auth.switchOTPTab("signup");
    }

    // =========================================================================
    // 1. Asynchronous OTP Login Submission Handler
    // =========================================================================
    var loginForm = document.getElementById("form_otp_login");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            var submitBtn = document.getElementById("btn_otp_submit");
            if (submitBtn) submitBtn.disabled = true;

            var identifierInput = document.getElementById("otp_login_identifier");
            var hiddenOtp = loginForm.querySelector('input[name="otp_code"]');
            var identifier = identifierInput ? identifierInput.value.trim() : "";
            var code = hiddenOtp ? hiddenOtp.value.trim() : "";
            var isEmail = identifier.includes("@");

            var phoneAction = loginForm.dataset.phoneAction || "/api/users/v1/auth/otp/sms/login/";
            var emailAction = loginForm.dataset.emailAction || "/api/users/v1/auth/otp/email/login/";
            var endpoint = isEmail ? emailAction : phoneAction;
            var payload = isEmail
                ? { email: identifier, otp_code: code }
                : { phone_number: identifier, otp_code: code };

            try {
                var csrfToken = (window.Core && Core.getCSRFToken) ? Core.getCSRFToken() : "";
                var res = await fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify(payload),
                });
                var data = await res.json();

                if (res.ok) {
                    if (window.Core && Core.authSession) {
                        if (data.access) {
                            Core.authSession.setCookie("access_token", data.access, data.access_expires_in || 3600);
                        }
                        if (data.refresh) {
                            Core.authSession.setCookie("refresh_token", data.refresh, 86400 * 7);
                        }
                    }

                    // Flow: Call customers API to fetch customer data & derive language preference
                    if (window.CustomerService && typeof window.CustomerService.onLoginSuccess === "function") {
                        try {
                            await window.CustomerService.onLoginSuccess();
                        } catch (custErr) {
                            console.debug("Customer fetch on login:", custErr);
                        }
                    }

                    var targetUrl = data.redirect_url || loginForm.dataset.redirectUrl || "/";
                    window.location.href = targetUrl;
                } else {
                    if (window.Core && Core.auth) {
                        Core.auth.showToast(data.detail || data.otp_code || data.email || data.phone_number || "Verification failed.");
                        if (typeof data.remaining_attempts !== "undefined") {
                            if (data.is_locked) {
                                Core.auth.setWarning("otp_login_attempts_warning", "Account locked. An unlock link has been emailed to you.");
                                if (submitBtn) submitBtn.disabled = true;
                                return;
                            } else {
                                Core.auth.setWarning(
                                    "otp_login_attempts_warning",
                                    "Warning: " + data.remaining_attempts + " remaining attempts before account lockout."
                                );
                            }
                        }
                    }
                    if (submitBtn) submitBtn.disabled = false;
                }
            } catch (err) {
                if (window.Core && Core.auth) {
                    Core.auth.showToast("Network error during OTP verification.");
                }
                if (submitBtn) submitBtn.disabled = false;
            }
        }, true);
    }

    // =========================================================================
    // 2. Asynchronous OTP Signup Submission Handler
    // =========================================================================
    var signupForm = document.getElementById("form_otp_signup");
    if (!signupForm) return;

    signupForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        var submitBtn = document.getElementById("btn_otp_signup_submit");
        if (submitBtn) submitBtn.disabled = true;

        var phoneInput = document.getElementById("otp_signup_phone");
        var hiddenOtp = signupForm.querySelector('input[name="signup_otp_code"]') ||
                        signupForm.querySelector('input[name="otp_code"]');
        var identifier = phoneInput ? phoneInput.value.trim() : "";
        var code = hiddenOtp ? hiddenOtp.value.trim() : "";

        if (!identifier || !code) {
            if (window.Core && Core.auth) {
                Core.auth.showToast("Please enter phone number and 6-digit verification code.");
            }
            if (submitBtn) submitBtn.disabled = false;
            return;
        }

        try {
            var csrfToken = (window.Core && Core.getCSRFToken) ? Core.getCSRFToken() : "";
            var firstNameInput = signupForm.querySelector('input[name="first_name"]');
            var lastNameInput = signupForm.querySelector('input[name="last_name"]');
            var emailInput = signupForm.querySelector('input[name="email"]');

            var payload = {
                identifier: identifier,
                code: code,
                channel: "phone"
            };
            if (firstNameInput && firstNameInput.value.trim()) {
                payload.first_name = firstNameInput.value.trim();
            }
            if (lastNameInput && lastNameInput.value.trim()) {
                payload.last_name = lastNameInput.value.trim();
            }
            if (emailInput && emailInput.value.trim()) {
                payload.email = emailInput.value.trim();
            }

            var res = await fetch("/api/users/v1/auth/otp/verify/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
            });
            var data = await res.json();

            if (res.ok) {
                if (window.Core && Core.authSession) {
                    if (data.access) {
                        Core.authSession.setCookie("access_token", data.access, data.access_expires_in || 3600);
                    }
                    if (data.refresh) {
                        Core.authSession.setCookie("refresh_token", data.refresh, 86400 * 7);
                    }
                }

                // Flow: Call customers API to fetch customer data & derive language preference
                if (window.CustomerService && typeof window.CustomerService.onLoginSuccess === "function") {
                    try {
                        await window.CustomerService.onLoginSuccess();
                    } catch (custErr) {
                        console.debug("Customer fetch on signup:", custErr);
                    }
                }

                var targetUrl = data.redirect_url || signupForm.dataset.redirectUrl || "/";
                window.location.href = targetUrl;
            } else {
                if (window.Core && Core.auth) {
                    Core.auth.showToast(data.detail || data.code || "Verification failed.");
                }
                if (submitBtn) submitBtn.disabled = false;
            }
        } catch (err) {
            if (window.Core && Core.auth) {
                Core.auth.showToast("Network error during verification. Please try again.");
            }
            if (submitBtn) submitBtn.disabled = false;
        }
    });
});
