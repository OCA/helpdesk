import re

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    Main migration function.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Backup the current 'number' field
    cr.execute("UPDATE helpdesk_ticket SET x_number_backup = number")

    # Get the sequence prefix
    sequence = env["ir.sequence"].search(
        [("code", "=", "helpdesk.ticket.sequence")], limit=1
    )
    if not sequence:
        return
    prefix = sequence.prefix

    # Prepare regex to match correct sequence numbers
    regex = re.compile(rf"^{re.escape(prefix)}\d+$")

    # Find tickets with incorrect 'number'
    tickets_to_update = env["helpdesk.ticket"].search([])
    for ticket in tickets_to_update:
        if not regex.match(ticket.number):
            # Assign a new number from the sequence
            new_number = env["ir.sequence"].next_by_code("helpdesk.ticket.sequence")
            ticket.write({"number": new_number})
