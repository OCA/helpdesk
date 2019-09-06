{
    'name': 'Helpdesk linker',
    'summary': 'Allow link any document to helpdesk tickets',
    'version': '11.0.1.8.0',
    'license': 'AGPL-3',
    'author': 'Domatix',
    'website': 'https://www.domatix.com/',
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
