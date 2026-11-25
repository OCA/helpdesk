# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_180


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_180.convert_company_dependent(
        env, "helpdesk.ticket.team", "default_project_id"
    )
    _convert_from_legacy_column(env)


def _convert_from_legacy_column(env):
    """Convert values coming from a plain (non company dependent) column.

    ``convert_company_dependent()`` only reads ``ir_property`` rows, which
    exist when the field was already company dependent before 18.0. When
    the database comes from a version where the field was a regular
    many2one, the values live in the integer column renamed by the
    pre-migration; assign them to the team's company (or the current
    company when the team has none).
    """
    legacy = openupgrade.get_legacy_name("default_project_id")
    if not openupgrade.column_exists(env.cr, "helpdesk_ticket_team", legacy):
        return
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE helpdesk_ticket_team t
        SET default_project_id = jsonb_build_object(
            COALESCE(t.company_id, %s)::text, t.{legacy}
        )
        WHERE t.{legacy} IS NOT NULL AND t.default_project_id IS NULL
        """,
        (env.company.id,),
    )
