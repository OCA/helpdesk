# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Motive",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Keep the motive ",
    "author": "Konos, "
              "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    "website": "https://githut.com/OCA/helpdesk",
    "depends": [
        "helpdesk_mgmt",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_motive.xml',
        'views/helpdesk_ticket.xml',
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": [
        "nelsonramirezs",
        "max3903",
    ],
}
