/** @odoo-module **/
// Copyright 2024 Nitrokey GmbH
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import FormEditorRegistry from "@website/js/form_editor_registry";
import {_t} from "@web/core/l10n/translation";

FormEditorRegistry.add("create_helpdesk_ticket", {
    formFields: [
        {
            type: "char",
            name: "partner_name",
            fillWith: "name",
            string: _t("Your Name"),
        },
        {
            type: "email",
            name: "partner_email",
            fillWith: "email",
            string: _t("Your E-Mail Address"),
        },
        {
            type: "many2one",
            name: "category_id",
            relation: "helpdesk.ticket.category",
            string: _t("Category"),
        },
        {
            type: "many2one",
            name: "team_id",
            relation: "helpdesk.ticket.team",
            string: _t("Support Team"),
        },
        {
            type: "char",
            modelRequired: true,
            name: "name",
            string: _t("Subject"),
        },
        {
            type: "html",
            required: true,
            name: "description",
            string: _t("Description"),
        },
    ],
    fields: [
        {
            name: "category_id",
            type: "many2one",
            relation: "helpdesk.ticket.category",
            string: _t("Category"),
            title: _t("Assign tickets to a category."),
        },
        {
            name: "team_id",
            type: "many2one",
            relation: "helpdesk.ticket.team",
            string: _t("Support Team"),
            title: _t("Assign tickets to a support team."),
        },
    ],
});
