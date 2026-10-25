/**
 * otp_signup.js: OTP Signup submission and tab switching handler.
 */
document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // Switch to initial tab if requested via data attribute
    var container = document.getElementById("otp_auth_container");
    var initialTab = container ? container.dataset.initialTab : "login";
    if (initialTab === "signup" && window.Core && Core.auth && typeof Core.auth.switchOTPTab === "function") {
        Core.auth.switchOTPTab("signup");
    }

    // Asynchronous OTP signup submission handler with cookie persistence & redirect
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
