{
    'name': 'Helpdesk link document',
    'summary': 'Allow link any document to helpdesk tickets',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Domatix, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/helpdesk',
    'depends': [
        'helpdesk_mgmt'
    ],
    'data': [
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_ticket_menu.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
}
