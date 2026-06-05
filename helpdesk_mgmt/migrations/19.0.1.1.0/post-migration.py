# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET helpdesk_mgmt_portal_select_category = true
        WHERE helpdesk_mgmt_portal_category_id_required""",
    )
