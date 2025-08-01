# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from openupgradelib import openupgrade
from psycopg2.sql import SQL, Identifier

from odoo import SUPERUSER_ID, api
from odoo.tools import column_exists, create_index, sql, table_exists

from odoo.addons.base.models.ir_module import Module, assert_log_admin_access

_logger = logging.getLogger(__name__)

TABLE_TO_CLONES = [
    ("helpdesk_ticket", "ee_helpdesk_ticket"),
    ("helpdesk_tag", "ee_helpdesk_tag"),
    ("helpdesk_ticket_type", "ee_helpdesk_ticket_type"),
    ("helpdesk_sla", "ee_helpdesk_sla"),
    ("helpdesk_sla_status", "ee_helpdesk_sla_status"),
    ("helpdesk_team", "ee_helpdesk_team"),
    ("helpdesk_stage", "ee_helpdesk_stage"),
    ("helpdesk_tag_helpdesk_ticket_rel", "ee_helpdesk_tag_helpdesk_ticket_rel"),
    ("helpdesk_team_res_users_rel", "ee_helpdesk_team_res_users_rel"),
    ("team_stage_rel", "ee_team_stage_rel"),
    ("helpdesk_sla_helpdesk_stage_rel", "ee_helpdesk_sla_helpdesk_stage_rel"),
    ("helpdesk_sla_helpdesk_tag_rel", "ee_helpdesk_sla_helpdesk_tag_rel"),
    (
        "helpdesk_sla_helpdesk_ticket_type_rel",
        "ee_helpdesk_sla_helpdesk_ticket_type_rel",
    ),
    ("helpdesk_sla_res_partner_rel", "ee_helpdesk_sla_res_partner_rel"),
    ("mail_alias", "ee_mail_alias"),
]

MODULE_TO_UNINSTALL = ["helpdesk"]


def _clone_table(cr, old_name, new_name):
    if not table_exists(cr, old_name):
        _logger.warning("Table %s does not exist, skipping.", old_name)
        return
    _logger.info("Cloning table %s to %s...", old_name, new_name)
    cr.execute(SQL("DROP TABLE IF EXISTS {} CASCADE").format(Identifier(new_name)))
    cr.execute(
        SQL("CREATE TABLE {} (LIKE {} INCLUDING ALL)").format(
            Identifier(new_name), Identifier(old_name)
        )
    )
    cr.execute(
        SQL("INSERT INTO {} SELECT * FROM {}").format(
            Identifier(new_name), Identifier(old_name)
        )
    )


def _uninstall_modules(env):
    modules = env["ir.module.module"].search(
        [
            ("name", "in", MODULE_TO_UNINSTALL),
            ("state", "=", "installed"),
        ]
    )
    if modules:
        _logger.info("Triggering uninstall for: %s", MODULE_TO_UNINSTALL)
        modules.sudo().button_uninstall()
    else:
        _logger.info("No EE 'helpdesk' modules currently installed.")


def _ensure_mail_tracking_index(cr):
    table_name = "mail_tracking_email"
    if not table_exists(cr, table_name):
        _logger.warning("Table %s does not exist, skipping.", table_name)
        return
    try:
        index_name = "mail_tracking_email_mail_id_index"
        expressions = ["mail_id"]
        create_index(cr, index_name, table_name, expressions)
    except Exception:
        _logger.exception("Failed to create index %s on %s", index_name, table_name)


def _drop_related_constraint(cr, table_name, constraint_name):
    definition = sql.constraint_definition(cr, table_name, constraint_name)
    if definition:
        _logger.info(
            "Dropping constraint %s on table %s: %s",
            constraint_name,
            table_name,
            definition,
        )
        try:
            sql.drop_constraint(cr, table_name, constraint_name)
        except Exception as e:
            _logger.error(
                "Failed to drop constraint %s on table %s: %s",
                constraint_name,
                table_name,
                str(e),
            )
    else:
        _logger.debug(
            "Constraint %s on table %s not found, skipping.",
            constraint_name,
            table_name,
        )


def _cleanup_helpdesk_references(env, cr):
    if "base.automation" in env:
        rules = (
            env["base.automation"]
            .with_context(active_test=False)
            .search([("model_id.model", "=", "helpdesk.ticket")])
        )
        if rules:
            _logger.info(
                "Deleting %s base.automation rules linked to helpdesk.ticket",
                len(rules),
            )
            rules.unlink()
    else:
        _logger.info("Model base.automation not found in registry, skipping cleanup.")

    if "mail.alias" in env:
        aliases = (
            env["mail.alias"]
            .with_context(active_test=False)
            .search([("alias_model_id.model", "=", "helpdesk.ticket")])
        )
        if aliases:
            _logger.info(
                "Deleting %s mail.alias linked to helpdesk.ticket", len(aliases)
            )
            aliases.unlink()
    else:
        _logger.info("Model mail.alias not found in registry, skipping cleanup.")


def rename_old_helpdesk_data(cr):
    _xmlids_renames = [
        (
            "helpdesk.mt_ticket_new",
            "helpdesk_mgmt.hlp_tck_created",
        ),
        # (
        #     "helpdesk.mt_ticket_stage",
        #     "helpdesk_mgmt.mt_ticket_stage",
        # ),
    ]
    _logger.info("Starting XMLID rename for legacy helpdesk records...")
    try:
        openupgrade.rename_xmlids(cr, _xmlids_renames)
        _logger.info(
            "Successfully renamed %d XMLIDs: %s",
            len(_xmlids_renames),
            ", ".join(f"{old} to {new}" for old, new in _xmlids_renames),
        )
    except Exception:
        _logger.exception("Failed to rename XMLIDs")


def add_old_res_id_per_mail_thread(cr, env):
    """Add 'old_res_id' field to mail.message, mail.followers, and ir.attachment
    if it doesn't already exist. Used to preserve reference before migration.
    """
    _logger.info("Checking for 'old_res_id' column on mail.thread-related tables...")

    models_to_update = [
        ("mail_message", "mail.message", "model"),
        ("mail_followers", "mail.followers", "res_model"),
        ("ir_attachment", "ir.attachment", "res_model"),
    ]

    for table, model, model_field in models_to_update:
        if not column_exists(env.cr, table, "old_res_id"):
            _logger.info("Adding 'old_res_id' column to %s (%s)...", table, model)
            try:
                field_spec = [
                    (
                        "old_res_id",
                        model,
                        table,
                        "integer",
                        "integer",
                        "helpdesk_mgmt",
                        False,
                    )
                ]
                openupgrade.add_fields(env, field_spec)
                _logger.info("Successfully added 'old_res_id' to %s", table)
                index_name = f"{table}_old_res_id_index"
                _logger.info(
                    "Creating index %s on %s(old_res_id) if not exists...",
                    index_name,
                    table,
                )
                try:
                    create_index(cr, index_name, table, ["old_res_id"])
                except Exception:
                    _logger.exception(
                        "Failed to create index %s on %s(old_res_id)", index_name, table
                    )
            except Exception:
                _logger.exception("Failed to add 'old_res_id' to %s", table)
        else:
            _logger.debug(
                "Column 'old_res_id' already exists in table %s. Skipping.", table
            )
        try:
            query = SQL(
                """
                UPDATE {table}
                SET old_res_id = res_id, {model_field} = 'archive.helpdesk'
                WHERE {model_field} = 'helpdesk.ticket'
            """
            ).format(table=Identifier(table), model_field=Identifier(model_field))
            openupgrade.logged_query(cr, query)
            _logger.info(
                "Initialized legacy records in %s for 'archive.helpdesk'", table
            )
        except Exception:
            _logger.exception("Failed to update old_res_id in %s", table)

    _logger.info("Finished adding 'old_res_id' columns.")


def drop_old_res_id(cr):
    """Drop 'old_res_id' columns from mail/thread-related tables if they exist."""
    column_spec = [
        ("mail_message", "old_res_id"),
        ("mail_followers", "old_res_id"),
        ("ir_attachment", "old_res_id"),
    ]
    _logger.info(
        "Starting cleanup: dropping legacy 'old_res_id' columns from %s",
        ", ".join(tbl for tbl, _ in column_spec),
    )
    try:
        openupgrade.drop_columns(cr, column_spec)
        _logger.info("Successfully dropped 'old_res_id' columns (if existed).")
    except Exception:
        _logger.exception("Failed to drop one or more 'old_res_id' columns.")


def pre_init_hook(cr):
    module = MODULE_TO_UNINSTALL[0]
    if not openupgrade.is_module_installed(cr, module):
        _logger.info("Skipping cloning: module '%s' is not installed.", module)
        return

    for old_name, new_name in TABLE_TO_CLONES:
        try:
            _clone_table(cr, old_name, new_name)
        except Exception as e:
            _logger.error("Failed to clone %s: %s", old_name, str(e))

    env = api.Environment(cr, SUPERUSER_ID, {})
    add_old_res_id_per_mail_thread(cr, env)
    rename_old_helpdesk_data(cr)


def post_init_hook(cr, registry):
    env = api.Environment(
        cr, SUPERUSER_ID, {"skip_remove_mail_message_and_followers": True}
    )
    module = MODULE_TO_UNINSTALL[0]
    if not openupgrade.is_module_installed(cr, module):
        _logger.info("Skipping cleanup: module '%s' is not installed.", module)
        return

    try:
        _ensure_mail_tracking_index(cr)

        CONSTRAINTS_TO_DROP = [
            ("helpdesk_team", "helpdesk_team_alias_id_fkey"),
            ("helpdesk_ticket", "helpdesk_ticket_stage_id_fkey"),
        ]
        for table, constraint in CONSTRAINTS_TO_DROP:
            _drop_related_constraint(cr, table, constraint)

        _cleanup_helpdesk_references(env, cr)

        _uninstall_modules(env)
    except Exception as e:
        _logger.error("Error post_init_hook: %s", str(e))


def uninstall_hook(cr, registry):
    _logger.info("Running uninstall_hook: cleaning up cloned tables...")

    for _, cloned_name in TABLE_TO_CLONES:
        if table_exists(cr, cloned_name):
            try:
                _logger.info("Dropping cloned table: %s", cloned_name)
                cr.execute(
                    SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                        Identifier(cloned_name)
                    )
                )
            except Exception as e:
                _logger.error("Failed to drop cloned table %s: %s", cloned_name, str(e))
        else:
            _logger.debug("Dropped table %s does not exist, skipping.", cloned_name)

    drop_old_res_id(cr)
    _logger.info("Cleanup after uninstall completed.")


def post_load_hook():
    @assert_log_admin_access
    def module_uninstall_new(self):
        """Perform the various steps required to uninstall a module completely
        including the deletion of all database structures created by the module:
        tables, columns, constraints, etc.
        """
        if not hasattr(self, "module_uninstall"):
            return self.module_uninstall_original()

        modules_to_remove = self.mapped("name")

        # start hooks
        self.env["ir.model.data"].with_context(
            skip_remove_mail_message_and_followers=True
        )._module_data_uninstall(modules_to_remove)
        # end hooks

        # we deactivate prefetching to not try to read a column that has been deleted
        self.with_context(prefetch_fields=False).write(
            {"state": "uninstalled", "latest_version": False}
        )
        return True

    if not hasattr(Module, "module_uninstall_original"):
        Module.module_uninstall_original = Module.module_uninstall
    Module.module_uninstall = module_uninstall_new
