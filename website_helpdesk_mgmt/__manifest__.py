# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2024 Nitrokey GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Website Helpdesk Mgmt",
    "version": "17.0.1.0.0",
    "category": "After-Sales",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["helpdesk_mgmt", "website"],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "data": [
        "data/ir_model_data.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "website.assets_wysiwyg": [
            "website_helpdesk_mgmt/static/src/js/website_helpdesk_form_editor.esm.js",
        ],
    },
    "maintainers": ["victoralmau"],
}
