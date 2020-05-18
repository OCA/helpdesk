# -*- coding: utf-8 -*-
{
    'name': "Timesheet for Helpdesk's Tickets",
    'summary': """
        Añade las funciones de partes de horas a los tickets de Helpdesk Management """,
    'author': "Inma Sánchez y Carlos Ramos",
    'website': "https://github.com/EDallas89",
    'category': 'After-Sales',
    'version': '12.0',
    'depends': ['helpdesk_mgmt', 'hr_timesheet','resource',],
    'data': [
        #'security/ir.model.access.csv',
        'views/helpdesk_ticket.xml',
        'views/helpdesk_team.xml',

    ],
    'installable': True,
    'application': True,
}