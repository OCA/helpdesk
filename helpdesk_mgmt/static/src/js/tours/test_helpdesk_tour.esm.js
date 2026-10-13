/** @odoo-module **/

import {registry} from "@web/core/registry";

function generateSteps() {
    const timestamp = Date.now();
    const numSubmits = 3;

    return [
        {
            trigger: 'form[action="/submitted/ticket"] input[name="subject"]',
            content: "Write subject",
            run: `edit Ticket Test ${timestamp}`,
        },
        {
            trigger: 'select[name="category"]',
            content: "Select category",
            run: ({anchor}) => {
                if (anchor.options.length > 1) {
                    anchor.selectedIndex = 1;
                    anchor.dispatchEvent(new Event("change", {bubbles: true}));
                }
            },
        },
        {
            trigger: 'textarea[name="description"]',
            content: "Write description",
            run: `edit Test description - ${timestamp}`,
        },
        {
            trigger: 'form[action="/submitted/ticket"] button.btn-primary',
            content: "Click submit multiple times quickly",
            run: ({anchor}) => {
                for (let i = 0; i < numSubmits; i++) {
                    anchor.click();
                }
            },
        },
        {
            trigger: "body:not(:has(form[action='/submitted/ticket']))",
            content: "Wait for redirect",
            timeout: 15000,
        },
    ];
}

registry.category("web_tour.tours").add("test_helpdesk_tour", {
    url: "/new/ticket",
    steps: generateSteps,
});
