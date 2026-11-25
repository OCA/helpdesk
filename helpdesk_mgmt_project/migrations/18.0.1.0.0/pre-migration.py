# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_TABLE = "helpdesk_ticket_team"
_COLUMN = "default_project_id"


@openupgrade.migrate()
def migrate(env, version):
    """Rename the legacy integer column before the ORM loads the field.

    ``default_project_id`` became ``company_dependent`` (stored as jsonb)
    in 18.0. A database migrated straight from a version where it was a
    regular many2one still has an integer column, and the ORM crashes
    trying to ``ALTER ... TYPE jsonb USING ...::jsonb``.
    """
    if not openupgrade.column_exists(env.cr, _TABLE, _COLUMN):
        return
    env.cr.execute(
        """
        SELECT data_type FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
        """,
        (_TABLE, _COLUMN),
    )
    row = env.cr.fetchone()
    if row and row[0] != "jsonb":
        openupgrade.rename_columns(env.cr, {_TABLE: [(_COLUMN, None)]})
