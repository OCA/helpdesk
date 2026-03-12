#    Copyright (C) 2020 Aresoltec Canarias <www.aresoltec.com>
#    Copyright (C) 2020 Punt Sistemes <www.puntsistemes.es.es>
#    Copyright (C) 2020 SDi Soluciones Digitales <www.sdi.es>
#    Copyright (C) 2020 Solvos Consultoría Informática <www.solvos.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Ticket Timesheet Time Control",
    "summary": "Add Time Controle to Helpdesk Management Timesheet.",
    "author": "Aresoltec Canarias, "
    "Punt Sistemes, "
    "SDi Soluciones Digitales, "
    "Solvos, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "After-Sales",
    "version": "18.0.1.1.3",
    "depends": [
        "helpdesk_mgmt_timesheet",
        "project_timesheet_time_control",
    ],
    "data": [
        "views/helpdesk_ticket_view.xml",
    ],
}
