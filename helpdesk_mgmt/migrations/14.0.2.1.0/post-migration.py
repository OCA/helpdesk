# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "helpdesk_mgmt", "migrations/14.0.2.1.0/noupdate_changes.xml"
    )
