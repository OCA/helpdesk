# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.ref("helpdesk_mgmt.group_helpdesk_user").implied_ids = [
        (
            6,
            0,
            [env.ref("helpdesk_mgmt.group_helpdesk_user_team").id],
        )
    ]
