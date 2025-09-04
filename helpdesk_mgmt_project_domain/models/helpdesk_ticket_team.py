# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr

DEFAULT_PYTHON_CODE = """# Available variables:
#  - ticket: Current helpdesk ticket record
#  - env: Odoo Environment
#  - user: Current user
#  - company: Current company
#  - AND, OR: Domain operators from odoo.osv.expression
#  - normalize: Function to normalize domain lists
#  - _: Translation function
#
# Your Python code will be automatically combined with static domains using AND.
# The code can either assign to 'domain' variable OR return a list directly.
#
# Example:
# if ticket.partner_id:
#     domain = [('commercial_partner_id', '=', ticket.commercial_partner_id.id)]

"""

DEFAULT_TASK_PYTHON_CODE = """# Available variables:
#  - ticket: Current helpdesk ticket record
#  - env: Odoo Environment
#  - user: Current user
#  - company: Current company
#  - AND, OR: Domain operators from odoo.osv.expression
#  - normalize: Function to normalize domain lists
#  - _: Translation function
#
# Your Python code will be automatically combined with static domains using AND.
# The code can either assign to 'domain' variable OR return a list directly.
#
# Example:
# if ticket.project_id:
#     domain = [('project_id', '=', ticket.project_id.id)]

"""


class HelpdeskTicketTeam(models.Model):

    _inherit = "helpdesk.ticket.team"

    project_domain = fields.Char(
        help="Domain to filter projects available for selection in tickets. "
        "This domain will be automatically combined with company domain using AND. "
        "Example: [('active', '=', True), ('partner_id', '!=', False)]",
    )

    project_domain_python = fields.Text(
        string="Project Domain Python Code",
        default=DEFAULT_PYTHON_CODE,
        help="Python code to generate dynamic project domain based on ticket data. "
        "This domain will be automatically combined with company and team domains using AND. "
        "The code can either assign to 'domain' variable OR return a list directly. "
        "Available variables: ticket, env, user, company, AND, OR, normalize.",
    )

    task_domain = fields.Char(
        help="Domain to filter tasks available for selection in tickets. "
        "This domain will be automatically combined with company domain using AND. "
        "Example: [('active', '=', True), ('project_id', '!=', False)]",
    )

    task_domain_python = fields.Text(
        string="Task Domain Python Code",
        default=DEFAULT_TASK_PYTHON_CODE,
        help="Python code to generate dynamic task domain based on ticket data. "
        "This domain will be automatically combined with company and team domains using AND. "
        "The code can either assign to 'domain' variable OR return a list directly. "
        "Available variables: ticket, env, user, company, AND, OR, normalize.",
    )

    @api.constrains("project_domain_python", "task_domain_python")
    def _check_python_code(self):
        """Validate Python domain code syntax and security using Odoo's native tools"""
        for record in self:
            # Check project domain python
            if record.project_domain_python:
                msg = test_python_expr(
                    expr=record.project_domain_python.strip(), mode="exec"
                )
                if msg:
                    raise ValidationError(_("Project Domain Python Code: %s") % msg)

            # Check task domain python
            if record.task_domain_python:
                msg = test_python_expr(
                    expr=record.task_domain_python.strip(), mode="exec"
                )
                if msg:
                    raise ValidationError(_("Task Domain Python Code: %s") % msg)

    def _get_eval_context(self, ticket=None):
        """Prepare the evaluation context for Python domain code execution"""

        def normalize(domain_list):
            """Helper function to normalize domain lists"""
            return expression.normalize_domain(domain_list)

        return {
            "ticket": ticket,
            "env": self.env,
            "user": self.env.user,
            "company": self.env.company,
            "AND": expression.AND,
            "OR": expression.OR,
            "normalize": normalize,
            "_": _,
        }

    def _execute_python_domain_code(self, python_code, ticket=None):
        """Execute Python domain code safely using Odoo's safe_eval"""
        if not python_code or not python_code.strip():
            return []

        eval_context = self._get_eval_context(ticket)

        try:
            # Use safe_eval to execute the Python code securely
            safe_eval(python_code.strip(), eval_context, mode="exec", nocopy=True)

            # Return the domain if it was assigned in the code
            return eval_context.get("domain", [])

        except Exception as e:
            # Log the error but don't raise it to avoid breaking the UI
            import logging

            _logger = logging.getLogger(__name__)
            _logger.warning(
                "Error executing Python domain code for team %s: %s", self.name, str(e)
            )
            return []
