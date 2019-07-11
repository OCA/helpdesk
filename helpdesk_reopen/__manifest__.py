# -*- coding: utf-8 -*-
# Author: Andrius Laukavičius. Copyright: JSC NOD Baltic
# Copyright 2019 Coop IT Easy SCRLfs
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk Reopen',
    'version': '12.0.0.1.0',
    'category': 'Helpdesk',
    'summary': 'Auto Helpdesk Reopen',
    'description': """
	Automatically reopens helpdesk queries if someone replies back to that query
	""",
    'author': 'OERP, Coop IT Easy SCRLfs',
    'website': 'www.oerp.eu',
    'depends': [
        'helpdesk',
        'mail',     
    ],
    'installable': True,
}
