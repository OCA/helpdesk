from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "helpdesk_ticket", "milestone_id"):
        openupgrade.add_fields(
            env,
            [
                (
                    "milestone_id",
                    "helpdesk.ticket",
                    "helpdesk_ticket",
                    "many2one",
                    False,
                    "helpdesk_mgmt_project",
                )
            ],
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE helpdesk_ticket ht
            SET milestone_id = pt.milestone_id
            FROM project_task pt
            WHERE pt.milestone_id IS NOT NULL AND ht.task_id = pt.id
            """,
        )
