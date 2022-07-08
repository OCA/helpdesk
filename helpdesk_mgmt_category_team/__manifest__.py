##############################################################################
#
#    Copyright 2022 initOS GmbH
#
##############################################################################
{
    "name": "Helpdesk Management Team",
    "summary": """
User will set Team in Helpdesk Category. Based on that,
when user create ticket from portal and select category,
system auto set Team from the selected category in Ticket.

    """,
    "category": "Helpdesk",
    "version": "15.0.1.0.0",
    "depends": ["helpdesk_mgmt", "base"],
    "data": [
        "views/helpdesk_ticket_category.xml",
    ],
    "author": "Nitrokey GmbH," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/helpdesk",
}
