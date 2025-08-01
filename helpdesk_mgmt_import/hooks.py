# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from random import randint

from openupgradelib import openupgrade_merge_records
from psycopg2 import sql

from odoo import SUPERUSER_ID, Command, api
from odoo.tools.misc import get_lang

logger = logging.getLogger(__name__)

EE_HELPDESK_TAG_TABLE = "ee_helpdesk_tag"
EE_HELPDESK_TICKET_TABLE = "ee_helpdesk_ticket"
EE_HELPDESK_TICKET_TYPE_TABLE = "ee_helpdesk_ticket_type"
EE_HELPDESK_TEAM_TABLE = "ee_helpdesk_team"
EE_HELPDESK_STAGE_TABLE = "ee_helpdesk_stage"
EE_HELPDESK_SLA_TABLE = "ee_helpdesk_sla"
EE_HELPDESK_TAG_HELPDESK_TICKET_REL_TABLE = "ee_helpdesk_tag_helpdesk_ticket_rel"
EE_SLA_TAG_REL_TABLE = "ee_helpdesk_sla_helpdesk_tag_rel"
EE_SLA_STAGE_REL_TABLE = "ee_helpdesk_sla_helpdesk_stage_rel"
EE_HELPDESK_TEAM_RES_USER_REL_TABLE = "ee_helpdesk_team_res_users_rel"
EE_TEAM_STAGE_REL_TABLE = "ee_team_stage_rel"


def _get_default_color():
    return randint(1, 11)


def _normalize_name(name):
    return (name or "").strip().lower()


def _next_sequence(env, model, field="sequence"):
    rec = env[model].search([], order=f"{field} DESC", limit=1)
    return (getattr(rec, field) or 0) + 1


def get_tables_with_prefix(cr, prefix):
    """
    Return list of existing tables/views/materialized views in the current schema
    whose names start with the given prefix.
    """
    query = """
        SELECT c.relname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r', 'v', 'm')
            AND n.nspname = current_schema
            AND c.relname LIKE %s
    """
    cr.execute(query, (f"{prefix}%",))
    return [row[0] for row in cr.fetchall()]


def _migrate_helpdesk_tag(cr, env, lang, ee_tables):
    migrate_table = EE_HELPDESK_TAG_TABLE
    if migrate_table not in ee_tables:
        logger.warning(
            f"Skipping helpdesk.tag migration: table {migrate_table} does not exist."
        )
        return {}

    logger.info("Migrating helpdesk.tag to helpdesk.ticket.tag...")
    query = sql.SQL("""SELECT id, name->>%s AS name, color FROM {}""").format(
        sql.Identifier(migrate_table)
    )
    cr.execute(query, (lang,))
    tag_rows = cr.fetchall()
    if not tag_rows:
        logger.info("No helpdesk.tag records to migrate.")
        return {}

    HelpdeskTicketTag = env["helpdesk.ticket.tag"]
    existing_name_map = {
        _normalize_name(t.name): t for t in HelpdeskTicketTag.search([])
    }
    tags_to_create = []
    tag_id_map = {}
    name_to_old_id = {}  # old_name -> new or existing tag

    for old_id, name, color in tag_rows:
        norm_name = _normalize_name(name)
        name_to_old_id[norm_name] = old_id
        if norm_name in existing_name_map:
            tag_id_map[old_id] = existing_name_map[norm_name]
            logger.info(
                f"Tag '{name}' (ID: {old_id}) already exists. Skipping creation."
            )
            continue
        tags_to_create.append(
            {
                "name": name.strip(),
                "color": color or _get_default_color(),
                "sequence": _next_sequence(env, HelpdeskTicketTag._name),
            }
        )

    if tags_to_create:
        try:
            created_tags = HelpdeskTicketTag.create(tags_to_create)
            for tag in created_tags:
                norm_name = _normalize_name(tag.name)
                old_id = name_to_old_id.get(norm_name)
                if old_id:
                    tag_id_map[old_id] = tag
            logger.info(
                f"Successfully created {len(created_tags)} helpdesk.ticket.tag."
            )
        except Exception:
            logger.exception("Error while creating helpdesk.ticket.tag records.")
    else:
        logger.info("No new helpdesk.tag to create.")

    return tag_id_map


def _migrate_helpdesk_ticket_type(cr, env, lang, ee_tables):
    migrate_table = EE_HELPDESK_TICKET_TYPE_TABLE
    if migrate_table not in ee_tables:
        logger.warning(
            f"Skipping helpdesk.ticket.type migration: table {migrate_table} does not exist."
        )
        return {}

    logger.info("Migrating helpdesk.ticket.type...")
    query = sql.SQL("SELECT id, name->>%s AS name FROM {}").format(
        sql.Identifier(migrate_table)
    )
    cr.execute(query, (lang,))
    type_rows = cr.fetchall()
    if not type_rows:
        logger.info("No helpdesk.ticket.type records to migrate.")
        return {}

    HelpdeskTicketType = env["helpdesk.ticket.type"]
    existing_name_map = {
        _normalize_name(t.name): t for t in HelpdeskTicketType.search([])
    }
    types_to_create = []
    type_id_map = {}
    name_to_old_id = {}
    for old_id, name in type_rows:
        if name and isinstance(name, (list, tuple)):
            name = name[0]
        norm_name = _normalize_name(name)
        name_to_old_id[norm_name] = old_id
        if norm_name in existing_name_map:
            logger.info(f"Type '{name}' already exists. Skipping.")
            type_id_map[old_id] = existing_name_map[norm_name]
            continue
        types_to_create.append({"name": name})

    if types_to_create:
        try:
            created_types = HelpdeskTicketType.create(types_to_create)
            for rec in created_types:
                norm_name = _normalize_name(rec.name)
                old_id = name_to_old_id.get(norm_name)
                if old_id:
                    type_id_map[old_id] = rec
            logger.info(
                f"Successfully created {len(created_types)} helpdesk.ticket.type."
            )
        except Exception:
            logger.exception("Error while creating helpdesk.ticket.type records.")
    else:
        logger.info("No new helpdesk.ticket.type to create.")

    return type_id_map


def _migrate_helpdesk_team(cr, env, lang, ee_tables):
    migrate_table = EE_HELPDESK_TEAM_TABLE
    if migrate_table not in ee_tables:
        logger.warning(
            f"Skipping helpdesk.team migration: table {migrate_table} does not exist.",
        )
        return {}

    logger.info("Migrating helpdesk.team to helpdesk.ticket.team...")
    query = sql.SQL(
        """SELECT id, name->>%s AS name, active, company_id,
            sequence, color, use_sla, alias_id
        FROM {}"""
    ).format(sql.Identifier(migrate_table))
    cr.execute(query, (lang,))
    team_rows = cr.fetchall()
    if not team_rows:
        logger.info("No helpdesk.team records to migrate.")
        return {}

    migrate_rel_table = EE_HELPDESK_TEAM_RES_USER_REL_TABLE
    team_to_user_ids = {}
    if migrate_rel_table in ee_tables:
        query = sql.SQL("SELECT helpdesk_team_id, res_users_id FROM {}").format(
            sql.Identifier(migrate_rel_table)
        )
        cr.execute(query)
        team_user_rows = cr.fetchall()
        for team_id, user_id in team_user_rows:
            team_to_user_ids.setdefault(team_id, []).append(user_id)

    HelpdeskTicketTeam = env["helpdesk.ticket.team"]
    MailAlias = env["mail.alias"]
    team_id_map = {}
    for (
        old_team_id,
        name,
        active,
        company_id,
        sequence,
        color,
        use_sla,
        old_alias_id,
    ) in team_rows:
        team_vals = {
            "name": name,
            "active": active,
            "company_id": company_id or env.company.id,
            "sequence": sequence or _next_sequence(env, HelpdeskTicketTeam._name),
            "color": color or _get_default_color(),
            "use_sla": use_sla,
        }
        user_ids = team_to_user_ids.get(old_team_id)
        if user_ids:
            team_vals["user_ids"] = [(6, 0, user_ids)]
        try:
            new_team = HelpdeskTicketTeam.create(team_vals)
            team_id_map[old_team_id] = new_team
        except Exception:
            logger.exception("Error creating helpdesk.ticket.team for %s", name)
            continue

        if old_alias_id and "ee_mail_alias" in ee_tables:
            query = sql.SQL(
                """SELECT alias_name, alias_contact, alias_defaults
                    FROM {} WHERE id = %s"""
            ).format(sql.Identifier("ee_mail_alias"))
            cr.execute(query, (old_alias_id,))
            row = cr.fetchone()
            if row:
                alias_name, alias_contact, alias_defaults = row
                alias_defaults = "{'team_id': %d}" % new_team.id
                alias_vals = {
                    "alias_name": alias_name or f"team_{new_team.id}",
                    "alias_model_id": env.ref("helpdesk_mgmt.model_helpdesk_ticket").id,
                    "alias_contact": alias_contact or "everyone",
                    "alias_defaults": alias_defaults,
                }
                try:
                    new_alias = MailAlias.create(alias_vals)
                    new_team.alias_id = new_alias.id
                    logger.info(
                        "Created alias '%s' for team %s (id=%s)",
                        new_alias.alias_name,
                        new_team.name,
                        new_team.id,
                    )
                except Exception:
                    logger.exception("Failed to create alias for team %s", name)
    logger.info(
        "Successfully migrated %s helpdesk.ticket.team records.", len(team_id_map)
    )
    return team_id_map


def _migrate_helpdesk_stage(cr, env, lang, team_id_map, ee_tables):
    migrate_table = EE_HELPDESK_STAGE_TABLE
    if migrate_table not in ee_tables:
        logger.warning(
            f"Skipping helpdesk.stage migration: table {migrate_table} does not exist."
        )
        return {}

    logger.info("Migrating helpdesk.stage to helpdesk.ticket.stage...")
    cr.execute(
        sql.SQL(
            """
            SELECT id, name->>%s AS name, description->>%s AS description,
            sequence, active, fold
            FROM {}
        """
        ).format(sql.Identifier(migrate_table)),
        (lang, lang),
    )
    stage_rows = cr.fetchall()
    if not stage_rows:
        logger.info("No helpdesk.stage records to migrate.")
        return {}

    HelpdeskTicketStage = env["helpdesk.ticket.stage"]

    migrate_rel_table = EE_TEAM_STAGE_REL_TABLE
    stage_to_team_ids = {}
    if migrate_rel_table in ee_tables:
        cr.execute(
            sql.SQL("SELECT helpdesk_team_id, helpdesk_stage_id FROM {}").format(
                sql.Identifier(migrate_rel_table)
            )
        )
        for team_id, stage_id in cr.fetchall():
            stage_to_team_ids.setdefault(stage_id, []).append(team_id)

    stage_id_map = {}
    vals_list = []
    mail_template = env.ref(
        "helpdesk_mgmt.changed_stage_template", raise_if_not_found=False
    )
    mail_template_id = mail_template.id if mail_template else False

    for stage_id, name, description, sequence, active, fold in stage_rows:
        old_team_ids = stage_to_team_ids.get(stage_id, [])
        new_team_ids = [
            team_id_map[tid].id for tid in old_team_ids if tid in team_id_map
        ]

        vals = {
            "name": name,
            "description": description if description else False,
            "sequence": sequence or _next_sequence(env, HelpdeskTicketStage._name),
            "active": active,
            "team_ids": [Command.set(new_team_ids)]
            if new_team_ids
            else [Command.clear()],
            "mail_template_id": mail_template_id,
            "closed": fold,
            "fold": fold,
        }
        vals_list.append((stage_id, vals))

    if vals_list:
        try:
            created_stages = HelpdeskTicketStage.create([v for _, v in vals_list])
            for (old_id, _), new_stage in zip(vals_list, created_stages):
                stage_id_map[old_id] = new_stage
            logger.info(
                f"Created {len(created_stages)} new helpdesk.ticket.stage records."
            )
        except Exception:
            logger.exception("Error while creating helpdesk.ticket.stage.")

    return stage_id_map


def _migrate_helpdesk_sla(
    cr, env, lang, team_id_map, tag_id_map, stage_id_map, ee_tables
):
    migrate_table = EE_HELPDESK_SLA_TABLE
    if migrate_table not in ee_tables:
        logger.warning(
            f"Skipping helpdesk.sla migration: table {migrate_table} does not exist."
        )
        return {}

    logger.info("Migrating helpdesk.sla...")
    cr.execute(
        sql.SQL(
            """
        SELECT id, name->>%s AS name, description->>%s AS description,
        active, team_id, stage_id, time
        FROM {}
    """
        ).format(sql.Identifier(migrate_table)),
        (lang, lang),
    )
    sla_rows = cr.fetchall()
    if not sla_rows:
        logger.info("No helpdesk.sla to migrate.")
        return {}

    HelpdeskSLA = env["helpdesk.sla"]
    sla_id_map = {}
    for (
        old_id,
        name,
        description,
        active,
        old_team_id,
        old_stage_id,
        time_hours,
    ) in sla_rows:
        team = team_id_map.get(old_team_id)
        hours_per_day = team.resource_calendar_id.hours_per_day if team else 8
        stage = stage_id_map.get(old_stage_id)
        hours_per_day = (
            team.resource_calendar_id.hours_per_day
            if team and team.resource_calendar_id
            else 8
        )
        days = int(time_hours // hours_per_day)
        hours = int(time_hours % hours_per_day)

        migrate_rel_table = EE_SLA_TAG_REL_TABLE
        tag_ids = []
        if migrate_rel_table in ee_tables:
            query = sql.SQL(
                "SELECT helpdesk_tag_id FROM {} WHERE helpdesk_sla_id = %s"
            ).format(sql.Identifier(migrate_rel_table))
            cr.execute(query, (old_id,))
            for (tag_old_id,) in cr.fetchall():
                if tag_old_id in tag_id_map:
                    tag_ids.append(tag_id_map[tag_old_id].id)
        # migrate legacy SLA-stage relations (exclude stages) -> ignore_stage_ids (M2M)

        migrate_stage_rel_table = EE_SLA_STAGE_REL_TABLE
        ignore_stage_ids = []
        if migrate_stage_rel_table in ee_tables:
            query = sql.SQL(
                "SELECT helpdesk_stage_id FROM {} WHERE helpdesk_sla_id = %s"
            ).format(sql.Identifier(migrate_stage_rel_table))
            cr.execute(query, (old_id,))
            for (stage_old_id,) in cr.fetchall():
                new_stage = stage_id_map.get(stage_old_id)
                if new_stage:
                    ignore_stage_ids.append(new_stage.id)
                else:
                    logger.debug(
                        "SLA %s: stage (old id=%s) from rel table not mapped; skipping",
                        old_id,
                        stage_old_id,
                    )

        vals = {
            "name": name,
            "note": description or "",
            "active": active,
            "days": days,
            "hours": hours,
            "team_ids": [Command.set([team.id])] if team else [],
            "tag_ids": [Command.set(tag_ids)],
            "stage_id": stage.id if stage else False,
        }
        if ignore_stage_ids:
            vals["ignore_stage_ids"] = [Command.set(ignore_stage_ids)]

        try:
            new_sla = HelpdeskSLA.create(vals)
            sla_id_map[old_id] = new_sla
        except Exception:
            logger.exception(f"Failed to create SLA '{name}'")

    logger.info(f"Created {len(sla_id_map)} helpdesk.sla records.")
    return sla_id_map


def _migrate_helpdesk_ticket(
    cr, env, lang, tag_id_map, ticket_type_map, team_id_map, stage_id_map, ee_tables
):
    migrate_table = EE_HELPDESK_TICKET_TABLE
    if migrate_table not in ee_tables:
        logger.warning(
            f"Skipping helpdesk.ticket migration: table {migrate_table} does not exist."
        )
        return {}

    logger.info("Migrating helpdesk.ticket records in batches...")
    HelpdeskTicket = env["helpdesk.ticket"]

    cr.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(migrate_table)))
    total = cr.fetchone()[0]
    if not total:
        logger.info("No helpdesk.ticket records to migrate.")
        return {}

    batch_size = 1000
    ticket_id_map = {}
    helpdesk_ticket_model_name = HelpdeskTicket._name
    archive_model_name = "archive.helpdesk"
    for offset in range(0, total, batch_size):
        end = min(offset + batch_size, total)
        logger.info(
            f"Migrating batch {offset // batch_size + 1} ({offset} - {end - 1})"
        )
        cr.execute(
            sql.SQL(
                """
            SELECT id, name, description, active, priority, kanban_state, color,
                team_id, ticket_type_id, stage_id,
                partner_id, partner_name, partner_email,
                user_id, assign_date, close_date, create_date
            FROM {}
            ORDER BY id
            LIMIT %s OFFSET %s
        """
            ).format(sql.Identifier(migrate_table)),
            (batch_size, offset),
        )
        ticket_rows = cr.fetchall()
        ticket_ids_batch = [row[0] for row in ticket_rows]
        tag_map = {}
        migrate_rel_table = EE_HELPDESK_TAG_HELPDESK_TICKET_REL_TABLE
        if migrate_rel_table in ee_tables and ticket_ids_batch:
            cr.execute(
                sql.SQL(
                    """
                    SELECT helpdesk_ticket_id, helpdesk_tag_id
                    FROM {}
                    WHERE helpdesk_ticket_id = ANY(%s)
                """
                ).format(sql.Identifier(migrate_rel_table)),
                (ticket_ids_batch,),
            )
            for tid, tag_old_id in cr.fetchall():
                tag_rec = tag_id_map.get(tag_old_id)
                if tag_rec:
                    tag_map.setdefault(tid, []).append(tag_rec.id)

        for row in ticket_rows:
            (
                old_id,
                name,
                description,
                active,
                priority,
                kanban_state,
                color,
                old_team_id,
                old_type_id,
                old_stage_id,
                partner_id,
                partner_name,
                partner_email,
                user_id,
                assign_date,
                close_date,
                create_date,
            ) = row
            description = (
                description.strip() if description else "Migrated from EE helpdesk"
            )
            team = team_id_map.get(old_team_id)
            type_rec = ticket_type_map.get(old_type_id) if old_type_id else None
            stage = stage_id_map.get(old_stage_id)
            tags = tag_map.get(old_id) or []

            vals = {
                "name": name,
                "description": description,
                "active": active,
                "priority": priority,
                "kanban_state": kanban_state,
                "color": color,
                "team_id": team.id if team else False,
                "type_id": type_rec.id if type_rec else False,
                "stage_id": stage.id if stage else False,
                "partner_id": partner_id,
                "partner_name": partner_name,
                "partner_email": partner_email,
                "user_id": user_id,
                "assigned_date": assign_date,
                "closed_date": close_date,
                "tag_ids": [Command.set(tags)] if tags else [Command.clear()],
                "create_date": create_date,
            }

            try:
                new_ticket = HelpdeskTicket.with_context(tracking_disable=True).create(
                    vals
                )
                ticket_id_map[old_id] = new_ticket
                new_ticket_id = new_ticket.id

                # 1. Reassign mail.message
                query = sql.SQL(
                    """
                    UPDATE {table}
                    SET res_id = %s, model = %s
                    WHERE old_res_id = %s AND model = %s
                """
                ).format(table=sql.Identifier("mail_message"))
                cr.execute(
                    query,
                    (
                        new_ticket_id,
                        helpdesk_ticket_model_name,
                        old_id,
                        archive_model_name,
                    ),
                )

                # 2. Reassign ir.attachment
                query = sql.SQL(
                    """
                    UPDATE {table}
                    SET res_id = %s, res_model = %s
                    WHERE old_res_id = %s AND res_model = %s
                """
                ).format(table=sql.Identifier("ir_attachment"))
                cr.execute(
                    query,
                    (
                        new_ticket_id,
                        helpdesk_ticket_model_name,
                        old_id,
                        archive_model_name,
                    ),
                )

                # 3. Safely reassign mail.followers (avoiding duplicates)
                query = sql.SQL(
                    """
                    SELECT id, partner_id FROM {table}
                    WHERE old_res_id = %s AND res_model = %s
                """
                ).format(table=sql.Identifier("mail_followers"))
                cr.execute(query, (old_id, archive_model_name))
                followers_to_update = cr.fetchall()

                if followers_to_update:
                    query = sql.SQL(
                        """
                        SELECT partner_id FROM {table}
                        WHERE res_id = %s AND res_model = %s
                    """
                    ).format(table=sql.Identifier("mail_followers"))
                    cr.execute(query, (new_ticket_id, helpdesk_ticket_model_name))
                    existing_partners = {row[0] for row in cr.fetchall()}

                    follower_ids_to_update = []
                    for fol_id, partner_id in followers_to_update:
                        if partner_id not in existing_partners:
                            follower_ids_to_update.append(fol_id)
                            existing_partners.add(partner_id)

                    if follower_ids_to_update:
                        query = sql.SQL(
                            """
                            UPDATE {table}
                            SET res_id = %s, res_model = %s
                            WHERE id = ANY(%s)
                        """
                        ).format(table=sql.Identifier("mail_followers"))
                        cr.execute(
                            query,
                            (
                                new_ticket_id,
                                helpdesk_ticket_model_name,
                                follower_ids_to_update,
                            ),
                        )

            except Exception as ex:
                logger.exception(f"Error creating ticket '{name}' (ID: {old_id}): {ex}")
                continue

    logger.info(f"Successfully created {len(ticket_id_map)} helpdesk.ticket records.")
    return ticket_id_map


def merge_duplicate_records_from_data_import(env):
    """
    Merge duplicate helpdesk stages created during data import & module installation.
    - Prefer keeping the stage with the highest ticket count.
    - If equal ticket count, prefer the one WITHOUT xml_id.
    """
    stage_xml_ids = [
        "helpdesk_mgmt.helpdesk_ticket_stage_new",
        "helpdesk_mgmt.helpdesk_ticket_stage_in_progress",
        "helpdesk_mgmt.helpdesk_ticket_stage_cancelled",
    ]

    Stage = env["helpdesk.ticket.stage"]
    Ticket = env["helpdesk.ticket"]
    IrModelData = env["ir.model.data"]
    for xml_id in stage_xml_ids:
        module_record = env.ref(xml_id, raise_if_not_found=False)
        if not module_record:
            continue

        record_name = module_record.name
        duplicates = Stage.search([("name", "=", record_name)])

        if len(duplicates) > 1:
            stage_with_counts = [
                (stage, Ticket.search_count([("stage_id", "=", stage.id)]))
                for stage in duplicates.filtered(lambda s: s.id != module_record.id)
            ]
            if not stage_with_counts:
                continue

            stage_with_counts.sort(key=lambda x: x[1], reverse=True)
            target_record = stage_with_counts[0][0]
            xid = IrModelData.search(
                [
                    ("module", "=", xml_id.split(".")[0]),
                    ("name", "=", xml_id.split(".")[1]),
                ]
            )
            if xid and xid.res_id != target_record.id:
                logger.info(
                    "Updating xml_id '%s' to point to record (ID %s)",
                    xml_id,
                    target_record.id,
                )
                try:
                    xid.write({"res_id": target_record.id})

                    logger.info(
                        "Merging duplicate stages for '%s': target=%s (tickets=%d) <- merge=%s",
                        record_name,
                        target_record.id,
                        stage_with_counts[0][1],
                        module_record.id,
                    )
                    openupgrade_merge_records.merge_records(
                        env=env,
                        model_name=Stage._name,
                        record_ids=module_record.ids,
                        target_record_id=target_record.id,
                        method="orm",
                    )

                    logger.info(
                        "Stage '%s' merged successfully. Kept ID=%s",
                        record_name,
                        target_record.id,
                    )
                except Exception:
                    logger.warning(
                        "Merge failed for %s. Falling back to XMLID reassignment only.",
                        xml_id,
                    )
                    # Remove XMLID association and delete duplicate
                    xid.write({"res_id": False})
                    module_record.unlink()  # delete duplicate was imported from depend module

                    # Finally reassign xmld to target_record
                    xid.write({"res_id": target_record.id})
                    logger.info(
                        "Fallback complete: Reassigned xml_id %s to (ID %s)",
                        xml_id,
                        target_record.id,
                    )
                except Exception:
                    logger.exception(f"Unexpected error during merge of {xml_id}")


def unlink_all_archive_helpdesk_data(env):
    archive_messages = env["mail.message"].search(
        [
            ("model", "=", "archive.helpdesk"),
        ]
    )
    logger.info(
        "Unlink mail.massage with model is archive.helpdesk %s", len(archive_messages)
    )
    archive_messages.unlink()
    archive_followers = env["mail.followers"].search(
        [
            ("res_model", "=", "archive.helpdesk"),
        ]
    )
    logger.info(
        "Unlink mail.followers with model is archive.helpdesk %s",
        len(archive_followers),
    )
    archive_followers.unlink()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    lang = get_lang(env).code or env.lang
    logger.info("Using language '%s' to migration...", lang)
    ee_tables = get_tables_with_prefix(cr, "ee_")
    try:
        helpdesk_module = env["ir.module.module"].search(
            [("name", "=", "helpdesk")], limit=1
        )
        if helpdesk_module and helpdesk_module.state != "uninstalled":
            logger.warning("helpdesk EE module still installed, skipping CE install.")
            return

        tag_id_map = _migrate_helpdesk_tag(cr, env, lang, ee_tables)
        type_id_map = _migrate_helpdesk_ticket_type(cr, env, lang, ee_tables)
        team_id_map = _migrate_helpdesk_team(cr, env, lang, ee_tables)
        stage_id_map = _migrate_helpdesk_stage(cr, env, lang, team_id_map, ee_tables)
        _migrate_helpdesk_sla(
            cr, env, lang, team_id_map, tag_id_map, stage_id_map, ee_tables
        )
        _migrate_helpdesk_ticket(
            cr, env, lang, tag_id_map, type_id_map, team_id_map, stage_id_map, ee_tables
        )
        merge_duplicate_records_from_data_import(env)
        unlink_all_archive_helpdesk_data(env)

        # Clear caches to avoid stale data issues
        logger.info("Caches invalidated and registry cleared after migration.")
        env.invalidate_all()
        env.registry.clear_caches()

        logger.info("Migration completed successfully.")

    except Exception as e:
        logger.exception(f"Error in post_init_hook: {e}")
        raise


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    logger.info("Running uninstall_hook: uninstall setup module...")
    setup_module = env["ir.module.module"].search(
        [
            ("name", "=", "helpdesk_mgmt_import_setup"),
            ("state", "=", "installed"),
        ]
    )
    if setup_module:
        logger.info("Triggering uninstall for: 'helpdesk_mgmt_import_setup'")
        setup_module.sudo().button_uninstall()
    else:
        logger.info("No 'helpdesk_mgmt_import_setup' modules currently installed.")
