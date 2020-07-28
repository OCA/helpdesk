#    Copyright (C) 2020 Aresoltec Canarias <www.aresoltec.com>
#    Copyright (C) 2020 Punt Sistemes <www.puntsistemes.es.es>
#    Copyright (C) 2020 SDi Soluciones Digitales <www.sdi.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk Ticket Timesheet',
    'summary': 'Add HR Timesheet to the tickets for Helpdesk Management.',
    'author': 'Aresoltec Canarias, '
              'Punt Sistemes, '
              'SDi Soluciones Digitales, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/helpdesk',
    'license': 'AGPL-3',
    'category': 'After-Sales',
    'version': '12.0.1.0.0',
    'depends': [
        'helpdesk_mgmt',
        'account',
    ],
    'data': [
        'views/helpdesk_team.xml',
        'views/helpdesk_ticket.xml',
    ]
}
