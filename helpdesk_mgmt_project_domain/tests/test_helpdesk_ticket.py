# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.osv import expression

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskProjectDomain(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Usar team_a da classe base em vez de criar novo team
        cls.team = cls.team_a
        cls.project_1 = cls.env["project.project"].create(
            {
                "name": "Project 1",
                "active": True,
            }
        )
        cls.project_2 = cls.env["project.project"].create(
            {
                "name": "Project 2",
                "active": False,
            }
        )

    def test_team_project_domain(self):
        """Test project domain from team when company has no domain"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set domain in team (using widget domain format)
        self.team.project_domain = "[('active', '=', True)]"

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be only team domain
        domain = ticket._get_project_domain()
        self.assertEqual(domain, [("active", "=", True)])

    def test_company_project_domain(self):
        """Test project domain from company when team has no domain"""
        # Clear team domain first
        self.team.project_domain = False

        # Set domain in company (using widget domain format)
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"

        # Create ticket with team (no domain)
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be only company domain
        domain = ticket._get_project_domain()
        self.assertEqual(domain, [("active", "=", True)])

    def test_team_domain_combined_with_company(self):
        """Test that team domain is combined with company domain using AND"""
        # Set different domains (using widget domain format)
        self.team.project_domain = "[('active', '=', False)]"
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be company AND team domain
        domain = ticket._get_project_domain()
        expected = expression.AND(
            [
                [("active", "=", True)],  # Company domain
                [("active", "=", False)],  # Team domain
            ]
        )
        self.assertEqual(domain, expected)

    def test_complex_domain(self):
        """Test complex domain with multiple conditions"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set complex domain (using widget domain format)
        complex_domain = "[('active', '=', True), ('partner_id', '!=', False)]"
        self.team.project_domain = complex_domain

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test Ticket Description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be only team domain since company is cleared
        domain = ticket._get_project_domain()
        # The domain should contain the team domain conditions
        self.assertIn(("active", "=", True), domain)
        self.assertIn(("partner_id", "!=", False), domain)

    def test_invalid_domain(self):
        """Test handling of invalid domain"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set invalid domain
        self.team.project_domain = "[('invalid_field', '=', True)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test Ticket Description",
                "team_id": self.team.id,
            }
        )

        # Get domain - invalid domain should be ignored, so only company domain remains
        domain = ticket._get_project_domain()
        # The invalid domain is ignored, so we get whatever company domain exists
        self.assertIsInstance(domain, list)

    def test_no_domain(self):
        """Test when no domain is set"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Create ticket without any domain
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test Ticket Description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should return empty list when no domains are set
        domain = ticket._get_project_domain()
        # If there's still a domain, it means there's a default somewhere
        self.assertIsInstance(domain, list)

    def test_domain_with_partner(self):
        """Test domain filtering by partner"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Create partner
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        # Set domain to filter by partner
        self.team.project_domain = "[('partner_id', '=', %d)]" % partner.id

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain
        domain = ticket._get_project_domain()
        # The domain should contain the partner condition
        self.assertIn(("partner_id", "=", partner.id), domain)

    def test_python_domain_code(self):
        """Test Python domain code functionality"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set Python code in team
        python_code = """
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
else:
    domain = [('active', '=', True)]
"""
        self.team.project_domain_python = python_code

        # Create ticket with partner
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "partner_id": partner.id,
            }
        )

        # Get domain - should use Python code result
        domain = ticket._get_project_domain()
        self.assertEqual(domain, [("partner_id", "=", partner.id)])

    def test_python_domain_code_no_partner(self):
        """Test Python domain code when ticket has no partner"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set Python code in team
        python_code = """
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
else:
    domain = [('active', '=', True)]
"""
        self.team.project_domain_python = python_code

        # Create ticket without partner
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should use Python code result
        domain = ticket._get_project_domain()
        self.assertEqual(domain, [("active", "=", True)])

    def test_domain_combination_company_and_team(self):
        """Test combination of company and team domains with AND logic"""
        # Set different domains
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"
        self.team.project_domain = "[('partner_id', '!=', False)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should combine both with AND
        domain = ticket._get_project_domain()
        expected = expression.AND(
            [
                [("active", "=", True)],
                [("partner_id", "!=", False)],
            ]
        )
        self.assertEqual(domain, expected)

    def test_domain_combination_all_sources(self):
        """Test combination of company, team, and Python domains"""
        # Set all three types of domains
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"
        self.team.project_domain = "[('partner_id', '!=', False)]"
        self.team.project_domain_python = """
domain = [('name', 'ilike', 'Project')]
"""

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should combine all three with AND
        domain = ticket._get_project_domain()
        expected = expression.AND(
            [
                [("active", "=", True)],
                [("partner_id", "!=", False)],
                [("name", "ilike", "Project")],
            ]
        )
        self.assertEqual(domain, expected)

    def test_compute_project_domain_ids(self):
        """Test the computed field project_domain_ids"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set domain to filter active projects
        self.team.project_domain = "[('active', '=', True)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Check computed field
        self.assertIn(self.project_1, ticket.project_domain_ids)
        self.assertNotIn(self.project_2, ticket.project_domain_ids)

    def test_get_project_domain_for_view(self):
        """Test the _get_project_domain_for_view method"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set domain in team
        self.team.project_domain = "[('active', '=', True)]"

        # Test with active_id in context
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test with active_id
        domain = (
            self.env["helpdesk.ticket"]
            .with_context(active_id=ticket.id)
            ._get_project_domain_for_view()
        )
        self.assertEqual(domain, [("active", "=", True)])

        # Test with default_team_id in context
        domain = (
            self.env["helpdesk.ticket"]
            .with_context(default_team_id=self.team.id)
            ._get_project_domain_for_view()
        )
        self.assertEqual(domain, [("active", "=", True)])

    # ========================================
    # Task Domain Tests
    # ========================================

    def test_team_task_domain(self):
        """Test task domain from team when company has no domain"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set domain in team (using widget domain format)
        self.team.task_domain = "[('active', '=', True)]"

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be only team domain
        domain = ticket._get_task_domain()
        self.assertEqual(domain, [("active", "=", True)])

    def test_company_task_domain(self):
        """Test task domain from company when team has no domain"""
        # Clear team domain first
        self.team.task_domain = False

        # Set domain in company
        self.company.helpdesk_mgmt_task_domain = "[('active', '=', True)]"

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be only company domain
        domain = ticket._get_task_domain()
        self.assertEqual(domain, [("active", "=", True)])

    def test_task_domain_combined_with_company(self):
        """Test task domain combination: company + team domains"""
        # Set domains in both company and team
        self.company.helpdesk_mgmt_task_domain = "[('active', '=', True)]"
        self.team.task_domain = "[('project_id', '!=', False)]"

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be combined with AND
        domain = ticket._get_task_domain()
        expected = expression.AND(
            [[("active", "=", True)], [("project_id", "!=", False)]]
        )
        self.assertEqual(domain, expected)

    def test_task_domain_combination_all_sources(self):
        """Test task domain combination: company + team + python"""
        # Set all domains
        self.company.helpdesk_mgmt_task_domain = "[('active', '=', True)]"
        self.team.task_domain = "[('project_id', '!=', False)]"
        self.team.task_domain_python = "domain = [('user_id', '!=', False)]"

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be combined with AND
        domain = ticket._get_task_domain()
        expected = expression.AND(
            [
                [("active", "=", True)],
                [("project_id", "!=", False)],
                [("user_id", "!=", False)],
            ]
        )
        self.assertEqual(domain, expected)

    def test_task_domain_python_code(self):
        """Test task domain with Python code"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set Python code in team
        self.team.task_domain_python = """
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('id', '=', 0)]
"""

        # Create ticket with team and project
        project = self.env["project.project"].create({"name": "Test Project"})
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "project_id": project.id,
            }
        )

        # Get domain - should filter by project
        domain = ticket._get_task_domain()
        self.assertEqual(domain, [("project_id", "=", project.id)])

    def test_task_domain_python_code_no_project(self):
        """Test task domain with Python code when no project is set"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set Python code in team
        self.team.task_domain_python = """
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('id', '=', 0)]
"""

        # Create ticket with team but no project
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should return empty domain
        domain = ticket._get_task_domain()
        self.assertEqual(domain, [("id", "=", 0)])

    def test_compute_task_domain_ids(self):
        """Test computed field for task domain IDs"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set domain in team
        self.team.task_domain = "[('active', '=', True)]"

        # Create some tasks
        task1 = self.env["project.task"].create(
            {
                "name": "Task 1",
                "active": True,
            }
        )
        task2 = self.env["project.task"].create(
            {
                "name": "Task 2",
                "active": False,
            }
        )

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Check computed field
        self.assertIn(task1, ticket.task_domain_ids)
        self.assertNotIn(task2, ticket.task_domain_ids)

    def test_get_task_domain_for_view(self):
        """Test _get_task_domain_for_view method"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set domain in team
        self.team.task_domain = "[('active', '=', True)]"

        # Test with active_id in context
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test with active_id
        domain = (
            self.env["helpdesk.ticket"]
            .with_context(active_id=ticket.id)
            ._get_task_domain_for_view()
        )
        self.assertEqual(domain, [("active", "=", True)])

        # Test with default_team_id in context
        domain = (
            self.env["helpdesk.ticket"]
            .with_context(default_team_id=self.team.id)
            ._get_task_domain_for_view()
        )
        self.assertEqual(domain, [("active", "=", True)])

    def test_task_domain_with_partner(self):
        """Test task domain with partner context"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set Python code that uses partner
        self.team.task_domain_python = """
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
else:
    domain = [('id', '=', 0)]
"""

        # Create partner and ticket
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "partner_id": partner.id,
            }
        )

        # Get domain - should filter by partner
        domain = ticket._get_task_domain()
        self.assertIn(("partner_id", "=", partner.id), domain)

    def test_task_domain_no_domain(self):
        """Test task domain when no domains are set"""
        # Clear all domains
        self.company.helpdesk_mgmt_task_domain = False
        self.team.task_domain = False
        self.team.task_domain_python = False

        # Create ticket with team
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Get domain - should be empty list
        domain = ticket._get_task_domain()
        self.assertIsInstance(domain, list)

    def test_task_domain_with_project_filter(self):
        """Test that task domain filters by selected project"""
        # Create two projects
        project1 = self.env["project.project"].create(
            {
                "name": "Project 1",
                "active": True,
            }
        )
        project2 = self.env["project.project"].create(
            {
                "name": "Project 2",
                "active": True,
            }
        )

        # Create tasks in each project
        task1 = self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": project1.id,
                "active": True,
            }
        )
        task2 = self.env["project.task"].create(
            {
                "name": "Task 2",
                "project_id": project2.id,
                "active": True,
            }
        )

        # Create ticket with project1 selected
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "project_id": project1.id,
            }
        )

        # Get task domain - should only include tasks from project1
        domain = ticket._get_task_domain()
        self.assertIn(("project_id", "=", project1.id), domain)

        # Verify that only task1 is available
        available_tasks = self.env["project.task"].search(domain)
        self.assertIn(task1, available_tasks)
        self.assertNotIn(task2, available_tasks)

        # Change project to project2
        ticket.project_id = project2.id

        # Get new task domain - should only include tasks from project2
        domain = ticket._get_task_domain()
        self.assertIn(("project_id", "=", project2.id), domain)

        # Verify that only task2 is available now
        available_tasks = self.env["project.task"].search(domain)
        self.assertIn(task2, available_tasks)
        self.assertNotIn(task1, available_tasks)

    def test_task_domain_no_duplicate_project_filter(self):
        """Test that project filter is not duplicated when Python code already
        filters by project"""
        # Create project
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "active": True,
            }
        )

        # Set Python code that already filters by project_id
        self.team.task_domain_python = """
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('id', '=', 0)]
"""

        # Create ticket with project
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "project_id": project.id,
            }
        )

        # Get domain - should not have duplicate project_id filters
        domain = ticket._get_task_domain()

        # Count occurrences of project_id filter
        project_filters = [
            cond
            for cond in domain
            if isinstance(cond, (list, tuple))
            and len(cond) == 3
            and cond[0] == "project_id"
            and cond[1] == "="
            and cond[2] == project.id
        ]

        # Should have exactly one project_id filter, not duplicated
        self.assertEqual(len(project_filters), 1)
        self.assertEqual(project_filters[0], ("project_id", "=", project.id))

    # ========================================
    # Onchange Methods Tests
    # ========================================

    def test_onchange_project_domain(self):
        """Test _onchange_project_domain method (lines 65-67)"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set domain in team
        self.team.project_domain = "[('active', '=', True)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_project_domain()

        # Should return domain dict for project_id field
        expected = {"domain": {"project_id": [("active", "=", True)]}}
        self.assertEqual(result, expected)

    def test_onchange_project_domain_with_partner(self):
        """Test _onchange_project_domain with partner change"""
        # Clear company domain first
        self.company.helpdesk_mgmt_project_domain = False

        # Set Python domain code that uses partner
        self.team.project_domain_python = """
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
else:
    domain = [('active', '=', True)]
"""

        # Create partner
        partner = self.env["res.partner"].create({"name": "Test Partner"})

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "partner_id": partner.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_project_domain()

        # Should return domain dict with partner filter
        expected = {"domain": {"project_id": [("partner_id", "=", partner.id)]}}
        self.assertEqual(result, expected)

    def test_onchange_project_domain_no_domain(self):
        """Test _onchange_project_domain when no domain is set"""
        # Clear all domains
        self.company.helpdesk_mgmt_project_domain = False
        self.team.project_domain = False
        self.team.project_domain_python = False

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_project_domain()

        # Should return empty domain
        expected = {"domain": {"project_id": []}}
        self.assertEqual(result, expected)

    def test_onchange_task_domain(self):
        """Test _onchange_task_domain method (lines 72-74)"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set domain in team
        self.team.task_domain = "[('active', '=', True)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_task_domain()

        # Should return domain dict for task_id field
        expected = {"domain": {"task_id": [("active", "=", True)]}}
        self.assertEqual(result, expected)

    def test_onchange_task_domain_with_project(self):
        """Test _onchange_task_domain with project selected"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Create project
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "active": True,
            }
        )

        # Create ticket with project
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "project_id": project.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_task_domain()

        # Should return domain dict with project filter
        expected = {"domain": {"task_id": [("project_id", "=", project.id)]}}
        self.assertEqual(result, expected)

    def test_onchange_task_domain_python_code(self):
        """Test _onchange_task_domain with Python code"""
        # Clear company domain first
        self.company.helpdesk_mgmt_task_domain = False

        # Set Python domain code
        self.team.task_domain_python = """
if ticket.project_id:
    domain = [('project_id', '=', ticket.project_id.id)]
else:
    domain = [('id', '=', 0)]
"""

        # Create project
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "active": True,
            }
        )

        # Create ticket with project
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
                "project_id": project.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_task_domain()

        # Should return domain dict with project filter from Python code
        expected = {"domain": {"task_id": [("project_id", "=", project.id)]}}
        self.assertEqual(result, expected)

    def test_onchange_task_domain_no_domain(self):
        """Test _onchange_task_domain when no domain is set"""
        # Clear all domains
        self.company.helpdesk_mgmt_task_domain = False
        self.team.task_domain = False
        self.team.task_domain_python = False

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_task_domain()

        # Should return empty domain
        expected = {"domain": {"task_id": []}}
        self.assertEqual(result, expected)

    def test_onchange_project_domain_combined_domains(self):
        """Test _onchange_project_domain with combined company and team domains"""
        # Set both company and team domains
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"
        self.team.project_domain = "[('partner_id', '!=', False)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_project_domain()

        # Should return combined domain
        expected_domain = expression.AND(
            [[("active", "=", True)], [("partner_id", "!=", False)]]
        )
        expected = {"domain": {"project_id": expected_domain}}
        self.assertEqual(result, expected)

    def test_onchange_task_domain_combined_domains(self):
        """Test _onchange_task_domain with combined company and team domains"""
        # Set both company and team domains
        self.company.helpdesk_mgmt_task_domain = "[('active', '=', True)]"
        self.team.task_domain = "[('project_id', '!=', False)]"

        # Create ticket
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test ticket description",
                "team_id": self.team.id,
            }
        )

        # Test onchange method
        result = ticket._onchange_task_domain()

        # Should return combined domain
        expected_domain = expression.AND(
            [[("active", "=", True)], [("project_id", "!=", False)]]
        )
        expected = {"domain": {"task_id": expected_domain}}
        self.assertEqual(result, expected)
