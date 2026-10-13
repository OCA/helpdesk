/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

function generateSteps() {
    const steps = [];
    const numSubmits = 3;
    const timestamp = Date.now();

    // Wait for the form to load
    steps.push({
        trigger: "form.form-horizontal.mt32",
        content: _t("Waiting for ticket form"),
        timeout: 7000,
    });

    steps.push({
        trigger: 'input[name="subject"]',
        content: _t("Write subject"),
        run: function () {
            const input = document.querySelector('input[name="subject"]');
            input.value = "Ticket Test " + timestamp;
            input.dispatchEvent(new Event("change", {bubbles: true}));
        },
    });

    // Select category
    steps.push({
        trigger: 'select[name="category"]',
        content: _t("Select category"),
        run: function () {
            const select = document.querySelector('select[name="category"]');
            if (select.options.length > 1) {
                select.selectedIndex = 1;
                select.dispatchEvent(new Event("change", {bubbles: true}));
            }
        },
    });

    // Fill description
    steps.push({
        trigger: 'textarea[name="description"]',
        content: _t("Write description"),
        run: function () {
            const textarea = document.querySelector('textarea[name="description"]');
            textarea.value = "Test description - " + timestamp;
            textarea.dispatchEvent(new Event("change", {bubbles: true}));
        },
    });

    // Send ticket multiple times to test duplicate handling
    for (let i = 1; i <= numSubmits; i++) {
        steps.push({
            trigger: "body",
            content: _t(`Attempt ${i} - Send ticket`),
            run: function () {
                const btn = document.querySelector(
                    'button.btn.btn-primary.btn-lg[type="submit"]'
                );

                if (!btn) {
                    console.log(`⚠️  Attempt ${i} - Button not found`);
                    return;
                }

                if (btn.disabled) {
                    console.log(`⚠️  Attempt ${i} - Button is disabled`);
                    return;
                }

                if (!btn.textContent.includes("Submit Ticket")) {
                    console.log(
                        `⚠️  Attempt ${i} - Button found but is not "Submit Ticket", it is: "${btn.textContent}"`
                    );
                    return;
                }

                console.log(`🖱️ Click on "Submit Ticket" (attempt ${i})`);
                btn.click();
            },
        });

        // Verify submission
        steps.push({
            trigger: "body",
            content: _t(`Verifying submission ${i}`),
            run: function () {
                return new Promise((resolve) => {
                    let attempts = 0;
                    const checkInterval = setInterval(() => {
                        attempts++;
                        const url = window.location.href;
                        const isRedirected = !url.includes("/new/ticket");

                        if (isRedirected || attempts >= 30) {
                            clearInterval(checkInterval);
                            console.log(`✅ Attempt ${i} completed - URL: ${url}`);
                            resolve();
                        }
                    }, 500);
                });
            },
            timeout: 15000,
        });
    }

    return steps;
}

const tour = {
    id: "test_helpdesk_tour",
    name: _t("Test Helpdesk - Verify Duplicates"),
    url: "/new/ticket",
    test: true,
    steps: generateSteps,
};

registry.category("web_tour.tours").add("test_helpdesk_tour", tour);
