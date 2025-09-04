# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskTicketTeam(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Usar team_a da classe base em vez de criar novo team
        cls.team = cls.team_a

    def test_valid_python_code(self):
        """Test valid Python code passes validation"""
        valid_code = """
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
else:
    domain = [('active', '=', True)]
"""
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": valid_code})

    def test_invalid_python_syntax(self):
        """Test invalid Python syntax raises ValidationError"""
        invalid_code = (
            "if ticket.partner_id domain = [('invalid', '=', True)]"  # Missing colon
        )

        with self.assertRaises(ValidationError) as context:
            self.team.write({"project_domain_python": invalid_code})

        self.assertIn("SyntaxError", str(context.exception))

    def test_empty_python_code(self):
        """Test that empty Python code passes validation"""
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": ""})

    def test_none_python_code(self):
        """Test that None Python code passes validation"""
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": False})

    def test_python_code_with_domain_assignment(self):
        """Test Python code that assigns domain variable"""
        domain_code = "domain = [('active', '=', True)]"
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": domain_code})

    def test_python_code_with_complex_logic(self):
        """Test complex but safe Python code"""
        complex_code = """
if ticket.partner_id:
    if ticket.partner_id.is_company:
        domain = [('partner_id', '=', ticket.partner_id.id)]
    else:
        domain = [('partner_id', '=', ticket.partner_id.parent_id.id)]
else:
    domain = [('active', '=', True)]
"""
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": complex_code})

    def test_python_code_with_available_variables(self):
        """Test Python code using available variables"""
        variables_code = """
domain = [('active', '=', True)]
if user.has_group('base.group_user'):
    domain.append(('user_id', '=', user.id))
if company:
    domain.append(('company_id', '=', company.id))
"""
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": variables_code})

    def test_python_code_with_dangerous_in_comments(self):
        """Test that dangerous operations in comments are ignored"""
        code_with_dangerous_comments = """
# This comment contains 'import os' but should be ignored
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
# Another comment with 'exec(' but should be ignored
else:
    domain = [('active', '=', True)]
"""
        # Should not raise any exception when writing
        self.team.write({"project_domain_python": code_with_dangerous_comments})

    # ========================================
    # Task Domain Tests
    # ========================================

    def test_valid_task_python_code(self):
        """Test valid task Python code passes validation"""
        valid_code = """
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('active', '=', True)]
"""
        # Should not raise any exception when writing
        self.team.write({"task_domain_python": valid_code})

    def test_invalid_task_python_syntax(self):
        """Test invalid task Python syntax raises ValidationError"""
        invalid_code = (
            "if ticket.project_id domain = [('invalid', '=', True)]"  # Missing colon
        )

        with self.assertRaises(ValidationError) as context:
            self.team.write({"task_domain_python": invalid_code})

        self.assertIn("SyntaxError", str(context.exception))

    def test_task_python_code_with_domain_assignment(self):
        """Test task Python code with domain assignment"""
        domain_code = """
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('active', '=', True)]
"""
        # Should not raise any exception when writing
        self.team.write({"task_domain_python": domain_code})

    def test_task_python_code_with_comments(self):
        """Test task Python code with comments containing dangerous operations"""
        code_with_dangerous_comments = """
# This is a comment with 'import os' but should be ignored
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
# Another comment with 'exec(' but should be ignored
else:
    domain = [('active', '=', True)]
"""
        # Should not raise any exception when writing
        self.team.write({"task_domain_python": code_with_dangerous_comments})

    def test_task_domain_field_creation(self):
        """Test that task_domain field can be set"""
        domain = "[('active', '=', True), ('project_id', '!=', False)]"
        self.team.write({"task_domain": domain})
        self.assertEqual(self.team.task_domain, domain)

    def test_task_domain_python_field_creation(self):
        """Test that task_domain_python field can be set"""
        python_code = "domain = [('active', '=', True)]"
        self.team.write({"task_domain_python": python_code})
        self.assertEqual(self.team.task_domain_python, python_code)

    # ========================================
    # Method Tests
    # ========================================

    def test_get_eval_context(self):
        """Test _get_eval_context method returns proper context"""
        # Test without ticket
        context = self.team._get_eval_context()
        self.assertIn("ticket", context)
        self.assertIn("env", context)
        self.assertIn("user", context)
        self.assertIn("company", context)
        self.assertIn("AND", context)
        self.assertIn("OR", context)
        self.assertIn("normalize", context)
        self.assertIn("_", context)
        self.assertIsNone(context["ticket"])
        self.assertEqual(context["user"], self.env.user)
        self.assertEqual(context["company"], self.env.company)

    def test_get_eval_context_with_ticket(self):
        """Test _get_eval_context method with ticket parameter"""
        # Create a test ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        context = self.team._get_eval_context(ticket)
        self.assertEqual(context["ticket"], ticket)
        self.assertIn("env", context)
        self.assertIn("user", context)
        self.assertIn("company", context)
        self.assertIn("AND", context)
        self.assertIn("OR", context)
        self.assertIn("normalize", context)
        self.assertIn("_", context)

    def test_execute_python_domain_code_empty(self):
        """Test _execute_python_domain_code with empty code"""
        result = self.team._execute_python_domain_code("")
        self.assertEqual(result, [])

        result = self.team._execute_python_domain_code(None)
        self.assertEqual(result, [])

        result = self.team._execute_python_domain_code("   ")
        self.assertEqual(result, [])

    def test_execute_python_domain_code_valid(self):
        """Test _execute_python_domain_code with valid code"""
        code = "domain = [('active', '=', True)]"
        result = self.team._execute_python_domain_code(code)
        self.assertEqual(result, [("active", "=", True)])

    def test_execute_python_domain_code_with_ticket(self):
        """Test _execute_python_domain_code with ticket context"""
        # Create a test ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        code = "domain = [('name', '=', ticket.name)]"
        result = self.team._execute_python_domain_code(code, ticket)
        self.assertEqual(result, [("name", "=", "Test Ticket")])

    def test_execute_python_domain_code_with_variables(self):
        """Test _execute_python_domain_code using context variables"""
        code = """
domain = [('active', '=', True)]
if user:
    domain.append(('user_id', '=', user.id))
if company:
    domain.append(('company_id', '=', company.id))
"""
        result = self.team._execute_python_domain_code(code)
        self.assertIn(("active", "=", True), result)
        self.assertIn(("user_id", "=", self.env.user.id), result)
        self.assertIn(("company_id", "=", self.env.company.id), result)

    def test_execute_python_domain_code_with_normalize(self):
        """Test _execute_python_domain_code using normalize function"""
        code = """
domain1 = [('active', '=', True)]
domain2 = [('user_id', '=', user.id)]
domain = normalize([domain1, domain2])
"""
        result = self.team._execute_python_domain_code(code)
        # The normalize function returns a normalized domain with & operators
        # Check that the result contains the expected structure
        self.assertTrue(len(result) > 0)
        # The result should be a normalized domain with & operator
        self.assertEqual(result[0], "&")
        # Check that both conditions are present in the normalized domain
        # The normalized domain structure is:
        #   ['&', (('active', '=', True),), (('user_id', '=', user_id),)]
        # So we need to check for tuples containing the conditions
        self.assertIn((("active", "=", True),), result)
        self.assertIn((("user_id", "=", self.env.user.id),), result)

    def test_execute_python_domain_code_invalid_syntax(self):
        """Test _execute_python_domain_code with invalid syntax returns empty list"""
        code = "invalid syntax here"
        result = self.team._execute_python_domain_code(code)
        self.assertEqual(result, [])

    def test_execute_python_domain_code_no_domain_assignment(self):
        """Test _execute_python_domain_code when no domain is assigned"""
        code = "x = 1 + 1"  # Valid code but no domain assignment
        result = self.team._execute_python_domain_code(code)
        self.assertEqual(result, [])

    # ========================================
    # Field Tests
    # ========================================

    def test_project_domain_field_creation(self):
        """Test that project_domain field can be set"""
        domain = "[('active', '=', True), ('partner_id', '!=', False)]"
        self.team.write({"project_domain": domain})
        self.assertEqual(self.team.project_domain, domain)

    def test_project_domain_python_default_value(self):
        """Test that project_domain_python has correct default value"""
        # Create a new team to test default value
        new_team = self.env["helpdesk.ticket.team"].create(
            {
                "name": "New Test Team",
                "alias_name": "new-test-team",
            }
        )

        # Check that default value is set
        self.assertTrue(new_team.project_domain_python)
        self.assertIn("Available variables:", new_team.project_domain_python)
        self.assertIn("ticket:", new_team.project_domain_python)
        self.assertIn("env:", new_team.project_domain_python)
        self.assertIn("user:", new_team.project_domain_python)
        self.assertIn("company:", new_team.project_domain_python)

    def test_task_domain_python_default_value(self):
        """Test that task_domain_python has correct default value"""
        # Create a new team to test default value
        new_team = self.env["helpdesk.ticket.team"].create(
            {
                "name": "New Test Team",
                "alias_name": "new-test-team",
            }
        )

        # Check that default value is set
        self.assertTrue(new_team.task_domain_python)
        self.assertIn("Available variables:", new_team.task_domain_python)
        self.assertIn("ticket:", new_team.task_domain_python)
        self.assertIn("env:", new_team.task_domain_python)
        self.assertIn("user:", new_team.task_domain_python)
        self.assertIn("company:", new_team.task_domain_python)

    def test_all_fields_can_be_set(self):
        """Test that all domain fields can be set simultaneously"""
        project_domain = "[('active', '=', True)]"
        project_python = "domain = [('active', '=', True)]"
        task_domain = "[('active', '=', True), ('project_id', '!=', False)]"
        task_python = "domain = [('project_id', '=', ticket.project_id.id)]"

        self.team.write(
            {
                "project_domain": project_domain,
                "project_domain_python": project_python,
                "task_domain": task_domain,
                "task_domain_python": task_python,
            }
        )

        self.assertEqual(self.team.project_domain, project_domain)
        self.assertEqual(self.team.project_domain_python, project_python)
        self.assertEqual(self.team.task_domain, task_domain)
        self.assertEqual(self.team.task_domain_python, task_python)

    # ========================================
    # Constraint Tests
    # ========================================

    def test_check_python_code_constraint_valid(self):
        """Test _check_python_code constraint with valid code"""
        # Should not raise any exception
        self.team._check_python_code()

    def test_check_python_code_constraint_invalid_syntax(self):
        """Test _check_python_code constraint with invalid syntax"""
        invalid_code = "if ticket.partner_id domain = [('invalid', '=', True)]"

        with self.assertRaises(ValidationError) as context:
            self.team.write({"project_domain_python": invalid_code})

        self.assertIn("Project Domain Python Code:", str(context.exception))

    def test_check_python_code_constraint_dangerous_operation(self):
        """Test _check_python_code constraint with dangerous operation"""
        dangerous_code = "import os; domain = []"

        with self.assertRaises(ValidationError) as context:
            self.team.write({"project_domain_python": dangerous_code})

        self.assertIn("Project Domain Python Code:", str(context.exception))

    def test_check_python_code_constraint_task_domain_invalid(self):
        """Test _check_python_code constraint with invalid task domain code"""
        invalid_code = "if ticket.project_id domain = [('invalid', '=', True)]"

        with self.assertRaises(ValidationError) as context:
            self.team.write({"task_domain_python": invalid_code})

        self.assertIn("Task Domain Python Code:", str(context.exception))

    def test_check_python_code_constraint_both_fields_invalid(self):
        """Test _check_python_code constraint with both fields invalid"""
        invalid_project_code = "if ticket.partner_id domain = [('invalid', '=', True)]"
        invalid_task_code = "if ticket.project_id domain = [('invalid', '=', True)]"

        with self.assertRaises(ValidationError) as context:
            self.team.write(
                {
                    "project_domain_python": invalid_project_code,
                    "task_domain_python": invalid_task_code,
                }
            )

        # Should raise error for the first invalid field encountered
        self.assertIn("Project Domain Python Code:", str(context.exception))

    def test_check_python_code_constraint_empty_fields(self):
        """Test _check_python_code constraint with empty fields"""
        # Should not raise any exception
        self.team.write(
            {
                "project_domain_python": "",
                "task_domain_python": "",
            }
        )
        self.team._check_python_code()

    def test_check_python_code_constraint_none_fields(self):
        """Test _check_python_code constraint with None fields"""
        # Should not raise any exception
        self.team.write(
            {
                "project_domain_python": False,
                "task_domain_python": False,
            }
        )
        self.team._check_python_code()
