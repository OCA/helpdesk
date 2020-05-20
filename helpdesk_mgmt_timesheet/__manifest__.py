##############################################################################
#    Copyright (C) 2020 Aresoltec Canarias <www.aresoltec.com>
#    Copyright (C) 2020 Punt Sistemes <www.puntsistemes.es.es>
#    Copyright (C) 2020 SDi Soluciones Digitales <www.sdi.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Helpdesk Ticket Timesheet',
    'summary': 'Add HR Timesheet to the tickets for Helpdesk Management.',
    'author': 'Aresoltec, '
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
