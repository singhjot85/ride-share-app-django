/**
 * carousel.js: Modular client-side controller for carousel & multi-step wizard components.
 *
 * Provides:
 * - CarouselComponent.goToStep(carouselId, step): activates specific slide/step.
 * - CarouselComponent.next(carouselId): advances to next step.
 * - CarouselComponent.prev(carouselId): goes back to previous step.
 */
(function (window, document) {
    "use strict";

    var instances = {};

    function initCarousel(container) {
        var carouselId = container.getAttribute("data-carousel-id") || container.id;
        if (!carouselId) return;

        var totalSteps = parseInt(container.getAttribute("data-total-steps") || "1", 10);
        var currentStep = parseInt(container.getAttribute("data-current-step") || "1", 10);

        instances[carouselId] = {
            element: container,
            currentStep: currentStep,
            totalSteps: totalSteps
        };
    }

    /**
     * Navigate carousel to target step.
     *
     * @param {string} carouselId
     * @param {number} targetStep
     */
    function goToStep(carouselId, targetStep) {
        var container = document.getElementById(carouselId);
        if (!container) return;

        var totalSteps = parseInt(container.getAttribute("data-total-steps") || "3", 10);
        if (targetStep < 1 || targetStep > totalSteps) return;

        // 1. Toggle Slides Visibility
        var slides = container.querySelectorAll(".carousel-slide");
        slides.forEach(function (slide) {
            var stepNum = parseInt(slide.getAttribute("data-slide-step"), 10);
            if (stepNum === targetStep) {
                slide.classList.remove("hidden");
                slide.classList.add("active");
            } else {
                slide.classList.add("hidden");
                slide.classList.remove("active");
            }
        });

        // 2. Update Progress Bars
        var progressBars = container.querySelectorAll(".carousel-progress-bar");
        progressBars.forEach(function (bar) {
            var stepIdx = parseInt(bar.getAttribute("data-step"), 10);
            if (stepIdx <= targetStep) {
                bar.classList.add("active", "bg-secondary");
                bar.classList.remove("bg-surface-container-high");
            } else {
                bar.classList.remove("active", "bg-secondary");
                bar.classList.add("bg-surface-container-high");
            }
        });

        // 3. Update Step Counter Text
        var counter = document.getElementById(carouselId + "-counter") || document.getElementById("stepCounterText");
        if (counter) {
            counter.textContent = targetStep + "/" + totalSteps;
        }

        container.setAttribute("data-current-step", targetStep);

        if (instances[carouselId]) {
            instances[carouselId].currentStep = targetStep;
        }

        // 4. Dispatch component lifecycle event
        var event = new CustomEvent("carousel:stepchange", {
            detail: {
                carouselId: carouselId,
                step: targetStep,
                totalSteps: totalSteps
            }
        });
        container.dispatchEvent(event);
    }

    function next(carouselId) {
        var inst = instances[carouselId];
        var cur = inst ? inst.currentStep : 1;
        goToStep(carouselId, cur + 1);
    }

    function prev(carouselId) {
        var inst = instances[carouselId];
        var cur = inst ? inst.currentStep : 1;
        goToStep(carouselId, cur - 1);
    }

    // Auto-initialize all carousels on DOM load
    document.addEventListener("DOMContentLoaded", function () {
        var carousels = document.querySelectorAll(".carousel-container");
        carousels.forEach(initCarousel);
    });

    // Public API
    window.CarouselComponent = {
        goToStep: goToStep,
        next: next,
        prev: prev,
        init: initCarousel
    };

    // Bridge for existing corridor wizard callbacks
    window.goToWizardStep = function (step) {
        goToStep("search-engine", step);
    };

})(window, document);
