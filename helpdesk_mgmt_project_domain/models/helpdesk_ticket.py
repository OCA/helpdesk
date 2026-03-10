# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    project_domain_ids = fields.Many2many(
        comodel_name="project.project",
        string="Available Projects",
        compute="_compute_project_domain_ids",
        help="Projects available for selection based on domain rules.",
    )

    task_domain_ids = fields.Many2many(
        comodel_name="project.task",
        string="Available Tasks",
        compute="_compute_task_domain_ids",
        help="Tasks available for selection based on domain rules.",
    )

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        domain="[('id', 'in', project_domain_ids)]",
    )

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        domain="[('id', 'in', task_domain_ids)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Sanitize project_id/task_id at create time (portal/API-safe)."""
        sanitized = []
        for vals in vals_list:
            vals = dict(vals or {})
            self._sanitize_domain_vals_inplace(vals)
            sanitized.append(vals)
        return super().create(sanitized)

    def _sanitize_domain_vals_inplace(self, vals):
        """
        If project_id/task_id is set but not allowed by the computed domain,
        drop them from vals before create.

        Uses sudo() only for checking existence/allowedness, to avoid portal ACL issues.
        """
        if isinstance(vals.get("project_id"), str) and vals["project_id"].isdigit():
            vals["project_id"] = int(vals["project_id"])
        if isinstance(vals.get("task_id"), str) and vals["task_id"].isdigit():
            vals["task_id"] = int(vals["task_id"])

        ticket = self.new(vals)

        company = ticket.company_id or ticket.team_id.company_id or self.env.company
        team = ticket.team_id

        project_id = vals.get("project_id")
        if project_id:
            domain = ticket._compute_project_domain_from_sources(
                team=team, company=company
            )
            if domain:
                ok = (
                    self.env["project.project"]
                    .sudo()
                    .search(
                        expression.AND([domain, [("id", "=", project_id)]]),
                        limit=1,
                    )
                )
                if not ok:
                    vals.pop("project_id", None)
                    vals.pop("task_id", None)
                    return

        task_id = vals.get("task_id")
        if task_id:
            if vals.get("project_id"):
                ticket.project_id = vals["project_id"]

            task_domain = ticket._compute_task_domain_from_sources(
                team=team, company=company
            )
            if task_domain:
                ok = (
                    self.env["project.task"]
                    .sudo()
                    .search(
                        expression.AND([task_domain, [("id", "=", task_id)]]),
                        limit=1,
                    )
                )
                if not ok:
                    vals.pop("task_id", None)

    @api.depends("team_id", "partner_id", "category_id", "priority", "company_id")
    def _compute_project_domain_ids(self):
        """Compute allowed projects for the current ticket state."""
        Project = self.env["project.project"]
        for ticket in self:
            company = ticket.company_id or ticket.team_id.company_id or self.env.company
            domain = ticket._compute_project_domain_from_sources(
                team=ticket.team_id, company=company
            )

            ticket.project_domain_ids = (
                Project.search(domain) if domain is not None else Project.browse([])
            )

    @api.depends(
        "team_id", "partner_id", "category_id", "priority", "company_id", "project_id"
    )
    def _compute_task_domain_ids(self):
        """Compute allowed tasks for the current ticket state."""
        Task = self.env["project.task"]
        for ticket in self:
            company = ticket.company_id or ticket.team_id.company_id or self.env.company
            domain = ticket._compute_task_domain_from_sources(
                team=ticket.team_id, company=company
            )

            ticket.task_domain_ids = (
                Task.search(domain) if domain is not None else Task.browse([])
            )

    @api.onchange("team_id", "partner_id", "category_id", "priority")
    def _onchange_project_domain(self):
        """Apply project domain when relevant fields change (single record)."""
        self.ensure_one()
        domain = self._get_project_domain_dynamic()
        if self.project_id and domain:
            ok = self.env["project.project"].search(
                expression.AND([domain, [("id", "=", self.project_id.id)]]),
                limit=1,
            )
            if not ok:
                self.project_id = False
                self.task_id = False
        return {"domain": {"project_id": domain}}

    @api.onchange("team_id", "partner_id", "category_id", "priority", "project_id")
    def _onchange_task_domain(self):
        """Apply task domain when relevant fields change (single record)."""
        self.ensure_one()
        domain = self._get_task_domain_dynamic()
        if self.task_id and domain:
            ok = self.env["project.task"].search(
                expression.AND([domain, [("id", "=", self.task_id.id)]]),
                limit=1,
            )
            if not ok:
                self.task_id = False
        return {"domain": {"task_id": domain}}

    def _get_project_domain(self):
        """Get the project domain for the current ticket."""
        self.ensure_one()
        return self._get_project_domain_dynamic()

    def _get_task_domain(self):
        """Get the task domain for the current ticket."""
        self.ensure_one()
        return self._get_task_domain_dynamic()

    @api.model
    def _get_project_domain_for_view(self):
        """
        Get project domain for view (used in domain attrs).
        Try active_id; if missing, use context defaults.
        """
        ctx = self.env.context
        active_id = ctx.get("active_id")

        if active_id:
            record = self.browse(active_id).exists()
            if record:
                return record._get_project_domain()

        team = None
        company = None

        if ctx.get("default_team_id"):
            team = (
                self.env["helpdesk.ticket.team"].browse(ctx["default_team_id"]).exists()
            )

        if ctx.get("default_company_id"):
            company = self.env["res.company"].browse(ctx["default_company_id"]).exists()

        if not company:
            company = self.env.company

        return self._compute_project_domain_from_sources(team=team, company=company)

    @api.model
    def _get_task_domain_for_view(self):
        """
        Get task domain for view (used in domain attrs).
        Try active_id; if missing, use context defaults.
        """
        ctx = self.env.context
        active_id = ctx.get("active_id")

        if active_id:
            record = self.browse(active_id).exists()
            if record:
                return record._get_task_domain()

        team = None
        company = None

        if ctx.get("default_team_id"):
            team = (
                self.env["helpdesk.ticket.team"].browse(ctx["default_team_id"]).exists()
            )

        if ctx.get("default_company_id"):
            company = self.env["res.company"].browse(ctx["default_company_id"]).exists()

        if not company:
            company = self.env.company

        return self._compute_task_domain_from_sources(team=team, company=company)

    def _safe_eval_domain_text(self, expr):
        """Evaluate textual domain with safe_eval and normalize; on error, return []."""
        if not expr:
            return []
        try:
            dom = safe_eval(expr, {"uid": self.env.uid})
            if isinstance(dom, list | tuple):
                return expression.normalize_domain(list(dom))
            _logger.warning(
                "Evaluated domain is not a list/tuple (expr=%s, type=%s)",
                expr,
                type(dom),
            )
        except Exception as e:
            _logger.error("Failed to evaluate static domain (expr=%s): %s", expr, e)
        return []

    def _run_python_domain(self, python_code, base_domain=None, company=None):
        """
        Execute controlled Python code to produce a domain.
        The script may ASSIGN `domain = [...]` OR directly RETURN the list.

        Available variables:
            - env, user, company, ticket, _
            - base_domain (already normalized list)
            - AND, OR, normalize (from odoo.osv.expression)
        """
        if not python_code:
            return []

        base_domain = expression.normalize_domain(base_domain or [])

        if company is None:
            if self and len(self) == 1:
                company = self.company_id or self.env.company
            else:
                company = self.env.company

        safe_globals = {
            "env": self.env,
            "user": self.env.user,
            "company": company,
            "ticket": self if (self and len(self) == 1) else self[:1],
            "_": _,
            "base_domain": base_domain,
            "AND": expression.AND,
            "OR": expression.OR,
            "normalize": expression.normalize_domain,
        }

        try:
            maybe = safe_eval(python_code.strip(), safe_globals)
            if isinstance(maybe, list | tuple):
                return expression.normalize_domain(list(maybe))
        except Exception as e:
            _logger.debug("Failed to evaluate Python domain as expression: %s", e)

        eval_context = dict(safe_globals)
        try:
            safe_eval(python_code.strip(), eval_context, mode="exec", nocopy=True)
            dom = eval_context.get("domain", [])
            if isinstance(dom, list | tuple):
                return expression.normalize_domain(list(dom))
            if dom:
                _logger.warning(
                    "Domain Python code assigned invalid type to 'domain': %s",
                    type(dom),
                )
        except Exception as e:
            _logger.error("Error executing domain Python code: %s", e)

        return []

    def _compute_project_domain_from_sources(self, team=None, company=None):
        """
        Combine all domains with AND:
          1) Company global domain
          2) Team static domain
          3) Team Python code
        """
        if self and len(self) == 1:
            team = team or self.team_id
            company = company or self.company_id or team.company_id
        company = company or self.env.company

        domains = []

        if company and getattr(company, "helpdesk_mgmt_project_domain", False):
            company_domain = self._safe_eval_domain_text(
                company.helpdesk_mgmt_project_domain
            )
            if company_domain:
                domains.append(company_domain)

        if team and getattr(team, "project_domain", False):
            team_domain = self._safe_eval_domain_text(team.project_domain)
            if team_domain:
                domains.append(team_domain)

        if team and getattr(team, "project_domain_python", False):
            python_domain = self._run_python_domain(
                team.project_domain_python, company=company
            )
            if python_domain:
                domains.append(python_domain)

        return expression.AND(domains) if domains else []

    def _compute_task_domain_from_sources(self, team=None, company=None):
        """
        Combine all domains with AND:
          1) Company global domain
          2) Team static domain
          3) Team Python code
          4) Project filter (if project is selected and no project filter exists yet)
        """
        if self and len(self) == 1:
            team = team or self.team_id
            company = company or self.company_id or team.company_id
        company = company or self.env.company

        domains = []

        if company and getattr(company, "helpdesk_mgmt_task_domain", False):
            company_domain = self._safe_eval_domain_text(
                company.helpdesk_mgmt_task_domain
            )
            if company_domain:
                domains.append(company_domain)

        if team and getattr(team, "task_domain", False):
            team_domain = self._safe_eval_domain_text(team.task_domain)
            if team_domain:
                domains.append(team_domain)

        if team and getattr(team, "task_domain_python", False):
            python_domain = self._run_python_domain(
                team.task_domain_python, company=company
            )
            if python_domain:
                domains.append(python_domain)

        if self and len(self) == 1 and self.project_id:
            already_filters_project = any(
                self._domain_contains_field(d, "project_id") for d in domains
            )
            if not already_filters_project:
                domains.append([("project_id", "=", self.project_id.id)])

        return expression.AND(domains) if domains else []

    def _get_project_domain_dynamic(self):
        """Single entrypoint for onchange and public calls."""
        self.ensure_one()
        return self._compute_project_domain_from_sources()

    def _get_task_domain_dynamic(self):
        """Single entrypoint for onchange and public calls."""
        self.ensure_one()
        return self._compute_task_domain_from_sources()

    def _domain_contains_field(self, domain, field_name):
        """True if domain contains any leaf referencing the given field name."""
        if not domain or not isinstance(domain, list | tuple):
            return False

        for token in domain:
            if isinstance(token, str):
                continue

            if isinstance(token, list | tuple):
                if len(token) == 3 and token[0] == field_name:
                    return True

                if len(token) > 0 and self._domain_contains_field(token, field_name):
                    return True

        return False
