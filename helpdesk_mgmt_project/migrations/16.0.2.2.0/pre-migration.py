# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists

column_renames = {
    "helpdesk_ticket_team": [("default_project_id", "old_default_project_id")],
}


@openupgrade.migrate()
def migrate(env, version):
    """Rename the column to keep the old value."""
    if column_exists(env.cr, "helpdesk_ticket_team", "default_project_id"):
        openupgrade.rename_columns(env.cr, column_renames)
