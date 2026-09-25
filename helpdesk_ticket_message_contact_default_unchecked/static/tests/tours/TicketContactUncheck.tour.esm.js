/* Copyright 2026 Solvos - Iria Alonso
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("helpdesk_suggested_recipient_tour", {
    test: true,
    url: "/odoo/my-helpdesk-tickets?view_type=list",
    steps: () => [
        {
            content: "Select the test ticket to open the form view",
            trigger:
                ".o_list_table .o_data_row:contains('Test Contact Uncheck') .o_data_cell",
            run: "click",
        },
        {
            content: "Click on Send message button to open the composer",
            trigger: "button.o-mail-Chatter-sendMessage",
            run: "click",
        },
        {
            content: "Check the suggested recipient is unchecked by default",
            trigger: ".form-check-input:not(:checked)",
        },
    ],
});
