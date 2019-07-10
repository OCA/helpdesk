{
    "name": "Helpdesk Timesheet",
    "summary": """
        Add Timesheets to the Helpdesk""",
    "category": "After-Sales",
    "version": "11.0.1.0.0",
    "depends": ["helpdesk_mgmt",
                "hr_timesheet"
    ],
    "data": [
        "views/helpdesk_view.xml",
        "views/hr_timesheet_view.xml",
        "views/helpdesk_ticket_stage_view.xml",
    ],
    "author": "Agent ERP GmbH, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "installable": True,
}
