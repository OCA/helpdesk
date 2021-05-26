# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Stage Auto",
    "summary": """
        Enables automatic stage change for tickets due to inactivity
    """,
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "After-Sales",
    "author": "Solvos, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt_timesheet",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "demo/helpdesk_ticket_stage_auto_demo.xml",
        "views/helpdesk_ticket_stage_views.xml",
    ],
}
