# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "helpdesk_mgmt",
        "migrations/15.0.1.0.0/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr, "helpdesk_mgmt", ["closed_ticket_template", "changed_stage_template"]
    )
