# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Mgmt Timesheet Time Control",
    "summary": "Helpdesk Management Timesheet Time Control",
    "version": "13.0.1.1.0",
    "license": "AGPL-3",
    "category": "Hidden",
    "author": "Graeme Gellatly,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt_timesheet",
        "project_timesheet_time_control",
        "helpdesk_mgmt_project",
    ],
    "data": ["views/helpdesk_ticket.xml"],
    "auto_install": True,
}
