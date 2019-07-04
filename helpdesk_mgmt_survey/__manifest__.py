# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk Survey',
    'summary': """
        Helpdesk Survey""",
    'license': 'AGPL-3',
    'category': 'After-Sales',
    'author': 'Domatix',
    'depends': [
        'helpdesk',
    ],
    'data': [
             'data/helpdesk_data.xml',
             'views/helpdesk_ticket_view.xml',
             'views/helpdesk_ticket_templates.xml',

    ],
    'installable': True,
}
