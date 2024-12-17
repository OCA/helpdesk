# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    """Set the default_project_id value in the project company."""
    if not column_exists(env.cr, "helpdesk_ticket_team", "old_default_project_id"):
        return
    env.cr.execute(
        """
        SELECT htt.id, htt.old_default_project_id, pp.company_id
        FROM helpdesk_ticket_team htt
        JOIN project_project pp ON htt.old_default_project_id = pp.id
        WHERE htt.old_default_project_id IS NOT NULL
        """
    )
    for team_id, old_default_project_id, company_id in env.cr.fetchall():
        team = env["helpdesk.ticket.team"].with_company(company_id).browse(team_id)
        team.write({"default_project_id": old_default_project_id})
