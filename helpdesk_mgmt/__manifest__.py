# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk Management',
    'summary': """
        Helpdesk""",
    'version': '11.0.1.0.2',
    'license': 'AGPL-3',
    'category': 'After-Sales',
    'author': 'AdaptiveCity, '
              'C2i Change 2 Improve, '
              'Domatix, '
              'Factor Libre, '
              'SDi Soluciones, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/helpdesk',
    'depends': [
        'mail',
        'portal',
    ],
    'data': [
        'data/helpdesk_data.xml',
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/helpdesk_ticket_templates.xml',
        'views/helpdesk_ticket_menu.xml',
        'views/helpdesk_ticket_team_view.xml',
        'views/helpdesk_ticket_stage_view.xml',
        'views/helpdesk_ticket_category_view.xml',
        'views/helpdesk_ticket_channel_view.xml',
        'views/helpdesk_ticket_tag_view.xml',
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_dashboard_view.xml',
    ],
    'demo': [
        'demo/helpdesk_demo.xml',
    ],
    'development_status': 'Alpha',
    'application': True,
    'installable': True,
}
