# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Stage Server Action",
    "summary": "Execute server actions when reaching a Helpdesk ticket stage",
    "version": "14.0.1.0.0",
    "category": "HelpDesk Service",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt"],
    "data": ["views/helpdesk_ticket_stage.xml"],
    "installable": True,
    "license": "AGPL-3",
}
