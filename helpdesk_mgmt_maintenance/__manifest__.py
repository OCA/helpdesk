# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Helpdesk Tickets Maintenance",
    "summary": "Links helpdesk tickets with maintenance equipments",
    "version": "15.0.1.0.0",
    "category": "After-Sales",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["helpdesk_mgmt", "maintenance"],
    "data": [
        "views/maintenance_equipment_views.xml",
        "views/helpdesk_ticket_views.xml",
    ],
}
