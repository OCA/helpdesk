# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    new_stage = env.ref(
        "helpdesk_mgmt.helpdesk_ticket_stage_new", raise_if_not_found=False
    )
    if new_stage and not new_stage.mail_template_id:
        new_stage.mail_template_id = env.ref(
            "helpdesk_mgmt.created_ticket_template", raise_if_not_found=False
        )
