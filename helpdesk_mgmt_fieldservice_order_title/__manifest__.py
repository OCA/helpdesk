{
    "name": "Helpdesk Field Service Order Title",
    "summary": "Display Field Service order titles on Helpdesk tickets and orders",
    "version": "18.0.1.0.2",
    "category": "Helpdesk",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["helpdesk_mgmt_fieldservice", "fieldservice_order_title"],
    "data": ["views/helpdesk_ticket_views.xml", "views/fsm_order_views.xml"],
    "installable": True,
}
