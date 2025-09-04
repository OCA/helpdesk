# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # ----------------------------
    # Computed fields for views
    # ----------------------------

    project_domain_ids = fields.Many2many(
        "project.project",
        string="Available Projects",
        compute="_compute_project_domain_ids",
        help="Projects available for selection based on domain rules",
    )

    task_domain_ids = fields.Many2many(
        "project.task",
        string="Available Tasks",
        compute="_compute_task_domain_ids",
        help="Tasks available for selection based on domain rules",
    )

    @api.depends("team_id", "partner_id", "category_id", "priority", "company_id")
    def _compute_project_domain_ids(self):
        """Compute available project IDs based on domain rules"""
        for record in self:
            domain = record._get_project_domain_dynamic()
            if domain:
                projects = self.env["project.project"].search(domain)
                record.project_domain_ids = projects
            else:
                record.project_domain_ids = self.env["project.project"]

    @api.depends(
        "team_id", "partner_id", "category_id", "priority", "company_id", "project_id"
    )
    def _compute_task_domain_ids(self):
        """Compute available task IDs based on domain rules"""
        for record in self:
            domain = record._get_task_domain_dynamic()
            if domain:
                tasks = self.env["project.task"].search(domain)
                record.task_domain_ids = tasks
            else:
                record.task_domain_ids = self.env["project.task"]

    # ----------------------------
    # Public API (views/onchange)
    # ----------------------------

    @api.onchange("team_id", "partner_id", "category_id", "priority")
    def _onchange_project_domain(self):
        """Apply project domain when relevant fields change (single record)."""
        self.ensure_one()
        domain = self._get_project_domain_dynamic()
        return {"domain": {"project_id": domain}}

    @api.onchange("team_id", "partner_id", "category_id", "priority", "project_id")
    def _onchange_task_domain(self):
        """Apply task domain when relevant fields change (single record)."""
        self.ensure_one()
        domain = self._get_task_domain_dynamic()
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

        # If we have an active record, use it
        if active_id:
            record = self.browse(active_id).exists()
            if record:
                return record._get_project_domain()

        # For new records or when no active_id, use context defaults
        team = None
        company = None

        # Try to get team from context
        if ctx.get("default_team_id"):
            team = (
                self.env["helpdesk.ticket.team"].browse(ctx["default_team_id"]).exists()
            )

        # Try to get company from context
        if ctx.get("default_company_id"):
            company = self.env["res.company"].browse(ctx["default_company_id"]).exists()

        # Fallback to current company
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

        # If we have an active record, use it
        if active_id:
            record = self.browse(active_id).exists()
            if record:
                return record._get_task_domain()

        # For new records or when no active_id, use context defaults
        team = None
        company = None

        # Try to get team from context
        if ctx.get("default_team_id"):
            team = (
                self.env["helpdesk.ticket.team"].browse(ctx["default_team_id"]).exists()
            )

        # Try to get company from context
        if ctx.get("default_company_id"):
            company = self.env["res.company"].browse(ctx["default_company_id"]).exists()

        # Fallback to current company
        if not company:
            company = self.env.company

        return self._compute_task_domain_from_sources(team=team, company=company)

    # ----------------------------
    # Internals
    # ----------------------------

    def _safe_eval_domain_text(self, expr):
        """Evaluate textual domain with safe_eval and normalize; on error, return []."""
        if not expr:
            return []
        try:
            dom = safe_eval(expr, {"uid": self.env.uid})
            if isinstance(dom, (list, tuple)):
                return expression.normalize_domain(list(dom))
            _logger.warning(
                "Evaluated domain is not a list/tuple (expr=%s, type=%s)",
                expr,
                type(dom),
            )
        except Exception as e:
            _logger.error("Failed to evaluate static domain (expr=%s): %s", expr, e)
        return []

    def _run_python_domain(self, python_code, base_domain=None):
        """
        Execute controlled Python code to produce a domain.
        The script may ASSIGN `domain = [...]` OR directly RETURN the list.
        Available variables:
            - env, user, company, ticket, fields, api, _
            - base_domain (already normalized list)
            - AND, OR, normalize (from odoo.osv.expression)
        """
        if not python_code:
            return []

        base_domain = expression.normalize_domain(base_domain or [])

        # Safe globals and helpers
        safe_globals = {
            "env": self.env,
            "user": self.env.user,
            "company": self.env.company,
            "ticket": self,  # current record
            "_": _,
            "base_domain": base_domain,
            "AND": expression.AND,
            "OR": expression.OR,
            "normalize": expression.normalize_domain,
        }

        # 1) Try as an expression that directly returns a domain
        try:
            maybe = safe_eval(python_code.strip(), safe_globals)
            if isinstance(maybe, (list, tuple)):
                return expression.normalize_domain(list(maybe))
        except Exception as e:
            # Fallback to exec mode below
            _logger.debug("Failed to evaluate Python domain as expression: %s", e)

        # 2) "Server action" style: script assigns `domain = [...]`
        eval_context = dict(safe_globals)
        try:
            safe_eval(python_code.strip(), eval_context, mode="exec", nocopy=True)
            dom = eval_context.get("domain", [])
            if isinstance(dom, (list, tuple)):
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
        Simplified logic - all domains are combined with AND:
          1) Company global domain (base filter)
          2) Team static domain (always AND with company)
          3) Team Python code (always AND with company + team)
        """
        # Allow usage without ensure_one() (e.g., view fallback)
        team = team or (self.team_id if self else None)
        company = company or (self.company_id if self else self.env.company)

        # Collect all domains to combine
        domains = []

        # 1) Company global domain (base filter)
        if company and getattr(company, "helpdesk_mgmt_project_domain", False):
            company_domain = self._safe_eval_domain_text(
                company.helpdesk_mgmt_project_domain
            )
            if company_domain:
                domains.append(company_domain)

        # 2) Team static domain (always AND with company)
        if team and getattr(team, "project_domain", False):
            team_domain = self._safe_eval_domain_text(team.project_domain)
            if team_domain:
                domains.append(team_domain)

        # 3) Team Python code (always AND with company + team)
        if team and getattr(team, "project_domain_python", False):
            python_domain = self._run_python_domain(team.project_domain_python)
            if python_domain:
                domains.append(python_domain)

        # Combine all domains with AND
        if domains:
            return expression.AND(domains)

        return []

    def _compute_task_domain_from_sources(self, team=None, company=None):
        """
        Simplified logic - all domains are combined with AND:
          1) Company global domain (base filter)
          2) Team static domain (always AND with company)
          3) Team Python code (always AND with company + team)
          4) Project filter (if project is selected)
        """
        # Allow usage without ensure_one() (e.g., view fallback)
        team = team or (self.team_id if self else None)
        company = company or (self.company_id if self else self.env.company)

        # Collect all domains to combine
        domains = []

        # 1) Company global domain (base filter)
        if company and getattr(company, "helpdesk_mgmt_task_domain", False):
            company_domain = self._safe_eval_domain_text(
                company.helpdesk_mgmt_task_domain
            )
            if company_domain:
                domains.append(company_domain)

        # 2) Team static domain (always AND with company)
        if team and getattr(team, "task_domain", False):
            team_domain = self._safe_eval_domain_text(team.task_domain)
            if team_domain:
                domains.append(team_domain)

        # 3) Team Python code (always AND with company + team)
        if team and getattr(team, "task_domain_python", False):
            python_domain = self._run_python_domain(team.task_domain_python)
            if python_domain:
                domains.append(python_domain)

        # 4) Project filter - filter tasks by selected project
        # Only add project filter if not already present in any domain
        if self and self.project_id:
            # Check if any existing domain already filters by project_id
            project_filter_exists = False
            for domain in domains:
                if self._domain_contains_project_filter(domain, self.project_id.id):
                    project_filter_exists = True
                    break

            if not project_filter_exists:
                domains.append([("project_id", "=", self.project_id.id)])

        # Combine all domains with AND
        if domains:
            return expression.AND(domains)

        return []

    def _get_project_domain_dynamic(self):
        """Single entrypoint for onchange and public calls."""
        self.ensure_one()
        return self._compute_project_domain_from_sources()

    def _get_task_domain_dynamic(self):
        """Single entrypoint for onchange and public calls."""
        self.ensure_one()
        return self._compute_task_domain_from_sources()

    def _domain_contains_project_filter(self, domain, project_id):
        """Check if domain already contains a filter for the specific project_id"""
        if not domain or not isinstance(domain, (list, tuple)):
            return False

        for condition in domain:
            if isinstance(condition, (list, tuple)) and len(condition) == 3:
                field, operator, value = condition
                if field == "project_id" and operator == "=" and value == project_id:
                    return True
            elif isinstance(condition, (list, tuple)) and len(condition) > 0:
                # Recursively check nested domains
                if self._domain_contains_project_filter(condition, project_id):
                    return True

        return False
