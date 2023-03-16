#    Copyright (C) 2023 XCG Consulting <https://orbeet.io/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Ticket Timesheet Time Type",
    "summary": "Add time type to the Timesheet of tickets in Helpdesk.",
    "author": "XCG Consulting, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "Project",
    "version": "15.0.1.0.0",
    "depends": [
        "helpdesk_mgmt_timesheet",
        "hr_timesheet_time_type",
    ],
    "data": [
        "views/helpdesk_ticket_view.xml",
    ],
}
