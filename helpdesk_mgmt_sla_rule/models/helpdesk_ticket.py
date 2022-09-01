# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sla_id = fields.Many2one("helpdesk.sla", string="SLA", compute="_compute_sla")

    def check_sla_rule_m2o(self, rule, check, field):
        if not rule[field] or not check:
            return True
        elif self[field].id == rule[field].id:
            return True
        else:
            return False

    def check_sla_rule_m2m(self, rule, check, field, match):
        if not rule[field] or not check or match == "none":
            return True
        elif match == "any" and bool(set(self[field].ids) & set(rule[field].ids)):
            return True
        elif match == "all" and sorted(self[field].ids) == sorted(rule[field].ids):
            return True
        else:
            return False

    def checks_sla_rule(self, sla_rule):
        check_team = self.check_sla_rule_m2o(rule=sla_rule, check=True, field="team_id")
        check_stage = self.check_sla_rule_m2o(
            rule=sla_rule, check=True, field="stage_id"
        )
        check_category = self.check_sla_rule_m2o(
            rule=sla_rule, check=sla_rule.match_categ, field="category_id"
        )
        check_type = self.check_sla_rule_m2o(
            rule=sla_rule, check=sla_rule.match_type, field="type_id"
        )
        check_tags = self.check_sla_rule_m2m(
            rule=sla_rule,
            check=sla_rule.match_tags,
            field="tag_ids",
            match=sla_rule.match_tags,
        )
        sla_rule_checks = [
            check_team,
            check_stage,
            check_category,
            check_type,
            check_tags,
        ]
        sla_rule_checks = set(sla_rule_checks)
        if len(sla_rule_checks) == 1:
            return True
        else:
            return False

    def _compute_sla(self):
        for record in self:
            if not record.team_id or record.team_id.use_sla_rule:
                sla_rules = record.env["sla.rule"].search([])
                sla_id = False
                for sla_rule in sla_rules:
                    if record.checks_sla_rule(sla_rule=sla_rule):
                        sla_id = sla_rule.sla_id
                        record.sla_id = sla_rule.sla_id.id
                        break
                if not sla_id:
                    _logger.warning(f"No SLA Rule found for ticket {record.name}.")
                    record.sla_id = False
            elif record.team_id:
                sla = record.env["helpdesk.sla"].search(
                    [("team_ids", "in", record.team_id.id)], limit=1
                )
                record.sla_id = sla.id if sla else False
            else:
                record.sla_id = False
