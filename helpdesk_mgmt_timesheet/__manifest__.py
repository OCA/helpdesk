#    Copyright (C) 2020 Aresoltec Canarias <www.aresoltec.com>
#    Copyright (C) 2020 Punt Sistemes <www.puntsistemes.es.es>
#    Copyright (C) 2020 SDi Soluciones Digitales <www.sdi.es>
#    Copyright (C) 2020 Solvos Consultoría Informática <www.solvos.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Ticket Timesheet",
    "summary": "Add HR Timesheet to the tickets for Helpdesk Management.",
    "author": "Aresoltec Canarias, "
    "Punt Sistemes, "
    "SDi Soluciones Digitales, "
    "Solvos, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "After-Sales",
    "version": "14.0.1.0.0",
    "depends": [
        "helpdesk_mgmt_project",
        "hr_timesheet",
        "project_timesheet_time_control",
    ],
    "data": [
        "views/helpdesk_team_view.xml",
        "views/helpdesk_ticket_view.xml",
        "views/hr_timesheet_view.xml",
        "report/report_timesheet_templates.xml",
    ],
    "demo": ["demo/helpdesk_mgmt_timesheet_demo.xml"],
}
