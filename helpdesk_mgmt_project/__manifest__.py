# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk Project',
    'summary': """
        Helpdesk""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'After-Sales',
    'author': 'PuntSistemes S.L.U., '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/helpdesk',
    'depends': [
        'helpdesk_mgmt',
        'project',
    ],
    'data': [
        'views/helpdesk_ticket_view.xml',
        'views/project_view.xml',
        'views/project_task_view.xml',
    ],
    'demo': [
    ],
    'development_status': 'Alpha',
    'application': False,
    'installable': True,
    'auto_install': True,
}
