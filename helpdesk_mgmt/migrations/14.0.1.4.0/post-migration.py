# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    closed_ticket_template = env.ref(
        "helpdesk_mgmt.closed_ticket_template", raise_if_not_found=False
    )
    if closed_ticket_template:
        closed_ticket_template.body_html = closed_ticket_template.body_html.replace(
            "${object.number}", '"${object.display_name}"'
        )
    changed_stage_template = env.ref(
        "helpdesk_mgmt.changed_stage_template", raise_if_not_found=False
    )
    if changed_stage_template:
        changed_stage_template.body_html = changed_stage_template.body_html.replace(
            "${object.number}", '"${object.display_name}"'
        )
