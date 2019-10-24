# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Website Helpdesk',
    'summary': """
        Create helpdesk tickets from website portal""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://www.kmee.com.br/',
    'depends': [
        'website_form',
        'helpdesk_mgmt',
    ],
    'data': [
        'data/website_data.xml'
    ],
    'demo': [
    ],
}
