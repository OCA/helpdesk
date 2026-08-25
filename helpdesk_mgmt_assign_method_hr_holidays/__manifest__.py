{
    "name": "helpdesk_mgmt_assign_method_hr_holidays",
    "summary": "Prevents users on leave from being assigned to helpdesk tickets.",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "Helpdesk",
    "version": "17.0.1.0.0",
    "depends": ["helpdesk_mgmt_assign_method", "hr_holidays"],
    "auto_install": True,
    "data": [
        "views/helpdesk_ticket_team_views.xml",
    ],
}
