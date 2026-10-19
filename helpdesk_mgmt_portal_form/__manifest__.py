# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Management Portal Form",
    "summary": """
        Replace the free-text portal description with structured, forms per category.
        """,
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "category": "After-Sales",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_form_views.xml",
        "views/helpdesk_ticket_menu.xml",
        "views/helpdesk_ticket_category_views.xml",
        "views/helpdesk_ticket_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "helpdesk_mgmt_portal_form/static/src/js/helpdesk_form_conditions.esm.js",
            "helpdesk_mgmt_portal_form/static/src/js/helpdesk_form.esm.js",
        ],
        "web.assets_unit_tests": [
            "helpdesk_mgmt_portal_form/static/src/js/helpdesk_form_conditions.esm.js",
            "helpdesk_mgmt_portal_form/static/tests/**/*.test.js",
        ],
    },
    "development_status": "Beta",
    "installable": True,
}
