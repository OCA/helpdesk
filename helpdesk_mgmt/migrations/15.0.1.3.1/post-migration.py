# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "helpdesk_mgmt", "migrations/15.0.1.3.1/noupdate_changes.xml"
    )
