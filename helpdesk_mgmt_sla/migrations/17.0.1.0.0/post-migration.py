from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Migrating helpdesk.sla
    for sla in env["helpdesk.sla"].search([]):
        if sla.ignore_stage_ids:
            sla.ignore_stage_ids = env["helpdesk.ticket.stage"].search(
                [
                    ("id", "not in", sla.ignore_stage_ids.ids),
                    "|",
                    ("team_ids", "=", False),
                    ("team_ids", "in", sla.team_ids.ids),
                ]
            )
        if not sla.stage_id:
            sla.stage_id = env["helpdesk.ticket.stage"].search(
                [
                    ("closed", "=", True),
                    "|",
                    ("team_ids", "=", False),
                    ("team_ids", "in", sla.team_ids.ids),
                ],
                limit=1,
            )
    # Generate helpdesk.ticket.sla -- We will create a dummy SLA for the tickets
    sla = env["helpdesk.sla"].create({"name": "migration SLA", "active": False})
    # Create the helpdesk.ticket.sla records for the SLA Failed closed tickets
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO helpdesk_ticket_sla (
            ticket_id,
            sla_id,
            create_date,
            write_date,
            create_uid,
            write_uid,
            state
        )
        SELECT
              ht.id,
              {sla.id} AS sla_id,
              NOW() AS create_date,
              NOW() AS write_date,
              ht.create_uid AS create_uid,
              ht.write_uid AS write_uid,
              'expired' AS state
        FROM helpdesk_ticket ht
        INNER JOIN helpdesk_ticket_stage hts ON ht.stage_id = hts.id
        WHERE ht.active = TRUE
           AND ht.sla_expired = TRUE
           AND hts.closed = TRUE
        """,
    )
    # Add the states for the accomplished tickets already closed
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO helpdesk_ticket_sla (
            ticket_id,
            sla_id,
            create_date,
            write_date,
            create_uid,
            write_uid,
            state
        )
        SELECT
              ht.id,
              {sla.id} AS sla_id,
              NOW() AS create_date,
              NOW() AS write_date,
              ht.create_uid AS create_uid,
              ht.write_uid AS write_uid,
              'accomplished' AS state
        FROM helpdesk_ticket ht
        INNER JOIN helpdesk_ticket_team htt ON ht.team_id = htt.id
        inner join helpdesk_ticket_stage hts ON hts.id = ht.stage_id
        WHERE ht.active = TRUE
          AND ht.sla_expired = FALSE
          AND htt.use_sla = TRUE
          AND hts.closed = TRUE
        """,
    )
    # Refresh the SLAs for the rest of tickets as there shouldn't be too many
    for ticket in env["helpdesk.ticket"].search(
        [("stage_id.closed", "=", False), ("team_id.use_sla", "=", True)]
    ):
        ticket.refresh_sla()
