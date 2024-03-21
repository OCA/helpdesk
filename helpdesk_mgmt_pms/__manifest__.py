# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Management PMS",
    "version": "14.0.1.0.0",
    "summary": """ Add the option to select property in the tickets. """,
    "author": "Irlui Ramirez, "
    "Consultores Hoteleros Integrales, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "category": "After-Sales",
    "depends": ["base", "web", "pms"],
    "data": ["views/assets.xml", "views/templates.xml"],
    "qweb": ["static/src/xml/*.xml"],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
