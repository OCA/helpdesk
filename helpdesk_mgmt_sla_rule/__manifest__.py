# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk SLA Rule",
    "summary": "Helpdesk SLA Rule",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "HelpDesk Service",
    "depends": ["helpdesk_mgmt_sla", "helpdesk_type"],
    "website": "https://github.com/OCA/helpdesk",
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_team.xml",
        "views/sla_rule.xml",
    ],
    "installable": True,
}
