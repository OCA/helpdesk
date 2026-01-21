# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import _, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    can_create_activity = fields.Boolean(related="team_id.allow_set_activity")
    res_model = fields.Char(string="Source Document Model", index=True)
    res_id = fields.Integer(string="Source Document", index=True)

    record_ref = fields.Reference(
        selection="_selection_record_ref",
        compute="_compute_record_ref",
        inverse="_inverse_record_ref",
        string="Source Record",
    )
    source_activity_type_id = fields.Many2one(comodel_name="mail.activity.type")
    date_deadline = fields.Date(string="Due Date", default=fields.Date.today)
    next_stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        compute="_compute_next_stage_id",
        store=True,
        index=True,
    )
    assigned_user_id = fields.Many2one(
        comodel_name="res.users",
    )
    is_new_stage = fields.Boolean(compute="_compute_is_new_stage")

    @api.model
    def _selection_record_ref(self):
        """Select target model for source document"""
        model_ids_str = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("helpdesk_mgmt_activity.helpdesk_available_model_ids", "[]")
        )
        model_ids = ast.literal_eval(model_ids_str)
        if not model_ids:
            return []
        IrModelAccess = self.env["ir.model.access"].with_user(self.env.user.id)
        available_models = self.env["ir.model"].search_read(
            [("id", "in", model_ids)], fields=["model", "name"]
        )
        return [
            (model.get("model"), model.get("name"))
            for model in available_models
            if IrModelAccess.check(model.get("model"), "read", False)
        ]

    @api.model
    def _get_team_stages(self, teams):
        """
        Get grouping stages by team id

        :param teams: helpdesk.ticket.team record set
        :return: dict {team_id: team stages recordset}
        """
        return {team.id: team._get_applicable_stages() for team in teams}

    def _compute_is_new_stage(self):
        for ticket in self:
            new_stage = ticket.team_id._get_applicable_stages()[:1]
            ticket.is_new_stage = ticket.stage_id == new_stage

    @api.depends("stage_id")
    def _compute_next_stage_id(self):
        """Compute next stage for ticket"""
        team_stages = self._get_team_stages(self.team_id)
        helpdesk_ticket_stage_obj = self.env["helpdesk.ticket.stage"]
        for record in self:
            current_stage = record.stage_id
            stages = team_stages.get(record.team_id.id, helpdesk_ticket_stage_obj)
            next_stage = (
                stages.filtered(
                    lambda stage, _cur_stage=current_stage: stage.sequence
                    > _cur_stage.sequence
                )[:1]
                or current_stage
            )
            record.next_stage_id = next_stage

    @api.depends("res_model", "res_id")
    def _compute_record_ref(self):
        """Compute Source Document Reference"""
        for rec in self:
            if not rec.res_model or not rec.res_id:
                rec.record_ref = None
                continue
            try:
                record = self.env[rec.res_model].browse(rec.res_id)
                record.check_access("read")
                rec.record_ref = f"{rec.res_model},{rec.res_id}"
            except Exception:
                rec.record_ref = None

    def _inverse_record_ref(self):
        """Set Source Document Reference"""
        for record in self:
            record_ref = record.record_ref
            record.write(
                {
                    "res_id": record_ref and record_ref.id or False,
                    "res_model": record_ref and record_ref._name or False,
                }
            )

    def set_next_stage(self):
        """Set next ticket stage"""
        for record in self:
            record.stage_id = record.next_stage_id

    def _check_activity_values(self):
        """Check activity values for helpdesk ticket"""
        if not self.can_create_activity:
            raise models.UserError(_("You cannot create activity!"))
        if not (self.res_id and self.res_model):
            raise models.UserError(_("Source Record is not set!"))
        if not self.source_activity_type_id:
            raise models.UserError(_("Activity Type is not set!"))
        if not self.date_deadline:
            raise models.UserError(_("Date Deadline is not set!"))
        if not self.assigned_user_id:
            raise models.UserError(_("Assigned User is not set!"))

    def perform_action(self):
        """Perform action for ticket"""
        self.ensure_one()
        # Check values for create activity
        self._check_activity_values()
        try:
            # Create activity for source record
            self.record_ref.activity_schedule(
                summary=self.name,
                note=self.description,
                date_deadline=self.date_deadline,
                activity_type_id=self.source_activity_type_id.id,
                ticket_id=self.id,
            )
            self.set_next_stage()
        except Exception as e:
            raise models.UserError from e
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": _("Activity has been created!"),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
