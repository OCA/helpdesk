# Copyright (C) 2021 - TODAY, Open Source Integrators
# Copyright (C) 2021 Pavlov Media
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Helpdesk - Field Service",
    "summary": "Create service requests from a ticket",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "author": "Odoo Community Association (OCA), Open Source Integrators, Pavlov Media",
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt", "fieldservice"],
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_views.xml",
        "views/fsm_location_views.xml",
        "views/fsm_order_views.xml",
        "views/res_partner.xml",
        "wizard/fsm_order_close_wizard.xml",
    ],
    "maintainers": [],
    "installable": True,
}
