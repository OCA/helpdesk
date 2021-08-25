{
    'name': 'Helpdesk Management Rating',
    'summary': """
        This module allows the customer to rate the assistance received
        on a ticket.
        """,
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Domatix',
    'website': 'https://www.domatix.com',
    'category': 'Productivity',
    'depends': ['helpdesk_mgmt', 'rating'],
    'data': [
        'data/helpdesk_data.xml',
        'views/helpdesk_ticket_menu.xml',
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_ticket_stage_view.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
}
