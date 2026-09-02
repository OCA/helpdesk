# Copyright 2025 Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Helpdesk Management Livechat",
    "summary": "Create ticket from livechat conversation",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "After-Sales",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago"],
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt", "im_livechat"],
    "data": [
        "data/utm_data.xml",
        "data/helpdesk_mgmt_livechat_chatbot_data.xml",
        "views/chatbot_script_views.xml",
        "views/chatbot_script_step_views.xml",
    ],
    "assets": {
        "mail.assets_messaging": [
            "helpdesk_mgmt_livechat/static/src/models/*.esm.js",
        ],
    },
    "auto_install": True,
}
