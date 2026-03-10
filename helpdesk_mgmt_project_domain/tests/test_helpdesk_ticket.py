# Copyright 2025 Marcel Savegnago - https://www.escodoo.com.br
# Copyright 2026 Kaynnan Lemes - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager

from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskProjectDomain(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.helpdesk_team = getattr(
            cls, "team_a", cls.env["helpdesk.ticket.team"].search([], limit=1)
        )
        cls.active_project = cls.env["project.project"].create(
            {"name": "Active Project", "active": True}
        )
        cls.inactive_project = cls.env["project.project"].create(
            {"name": "Inactive Project", "active": False}
        )

    def _reset_domain_configuration(self):
        self.company.helpdesk_mgmt_project_domain = False
        self.company.helpdesk_mgmt_task_domain = False
        self.helpdesk_team.project_domain = False
        self.helpdesk_team.project_domain_python = False
        self.helpdesk_team.task_domain = False
        self.helpdesk_team.task_domain_python = False

    def _create_ticket_minimal(self, **ticket_values):
        values = {
            "name": ticket_values.pop("name", "T"),
            "description": ticket_values.pop("description", "Test ticket description"),
            "team_id": ticket_values.pop("team_id", self.helpdesk_team.id),
        }
        values.update(ticket_values)
        return self.env["helpdesk.ticket"].create(values)

    @contextmanager
    def _mute_helpdesk_ticket_logger(self):
        logger = logging.getLogger(
            "odoo.addons.helpdesk_mgmt_project_domain.models.helpdesk_ticket"
        )
        previous_level = logger.level
        previous_propagate = logger.propagate
        try:
            logger.setLevel(logging.CRITICAL)
            logger.propagate = False
            yield
        finally:
            logger.setLevel(previous_level)
            logger.propagate = previous_propagate

    def test_field_domains_are_bound_to_computed_domain_ids(self):
        field_domain_cases = [
            ("project_id", "[('id', 'in', project_domain_ids)]"),
            ("task_id", "[('id', 'in', task_domain_ids)]"),
        ]
        for field_name, expected_domain in field_domain_cases:
            with self.subTest(field=field_name):
                field = self.env["helpdesk.ticket"]._fields[field_name]
                self.assertEqual(field.domain, expected_domain)

    def test_project_domain_sources_static_and_combined(self):
        self._reset_domain_configuration()
        self.helpdesk_team.project_domain = "[('active', '=', True)]"
        team_only_ticket = self._create_ticket_minimal(name="T_team_only")
        self.assertEqual(
            team_only_ticket._get_project_domain(), [("active", "=", True)]
        )
        self.assertIn(self.active_project, team_only_ticket.project_domain_ids)
        self.assertNotIn(self.inactive_project, team_only_ticket.project_domain_ids)

        self._reset_domain_configuration()
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"
        company_only_ticket = self._create_ticket_minimal(name="T_company_only")
        self.assertEqual(
            company_only_ticket._get_project_domain(), [("active", "=", True)]
        )

        self._reset_domain_configuration()
        self.company.helpdesk_mgmt_project_domain = "[('active', '=', True)]"
        self.helpdesk_team.project_domain = "[('name', 'ilike', 'Project')]"
        combined_sources_ticket = self._create_ticket_minimal(name="T_both_sources")
        expected_combined_domain = expression.AND(
            [
                [("active", "=", True)],
                [("name", "ilike", "Project")],
            ]
        )
        self.assertEqual(
            combined_sources_ticket._get_project_domain(), expected_combined_domain
        )

    def test_project_domain_python_and_safe_eval_error_paths(self):
        self._reset_domain_configuration()
        self.helpdesk_team.project_domain_python = """
if ticket.partner_id:
    domain = [('partner_id', '=', ticket.partner_id.id)]
else:
    domain = [('active', '=', True)]
"""
        partner = self.env["res.partner"].create({"name": "Partner A"})
        partner_ticket = self._create_ticket_minimal(
            name="T_py_partner", partner_id=partner.id
        )
        self.assertEqual(
            partner_ticket._get_project_domain(), [("partner_id", "=", partner.id)]
        )

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain_python = "[('active', '=', True)]"
        python_expression_ticket = self._create_ticket_minimal(name="T_py_expr_return")
        self.assertEqual(
            python_expression_ticket._get_project_domain(), [("active", "=", True)]
        )

        self._reset_domain_configuration()
        self.company.helpdesk_mgmt_project_domain = "'not a domain'"
        invalid_static_type_ticket = self._create_ticket_minimal(
            name="T_invalid_safe_eval_type"
        )
        with self._mute_helpdesk_ticket_logger():
            self.assertEqual(invalid_static_type_ticket._get_project_domain(), [])

        self._reset_domain_configuration()
        self.company.helpdesk_mgmt_project_domain = "[('active' = True)]"
        invalid_static_syntax_ticket = self._create_ticket_minimal(
            name="T_invalid_safe_eval_syntax"
        )
        with self._mute_helpdesk_ticket_logger():
            self.assertEqual(invalid_static_syntax_ticket._get_project_domain(), [])

        self._reset_domain_configuration()
        safe_eval_helper_ticket = self._create_ticket_minimal(name="T_safe_eval_empty")
        self.assertEqual(safe_eval_helper_ticket._safe_eval_domain_text(False), [])
        self.assertEqual(safe_eval_helper_ticket._safe_eval_domain_text(""), [])
        tuple_domain = safe_eval_helper_ticket._safe_eval_domain_text(
            "(('active', '=', True),)"
        )
        self.assertEqual(tuple_domain, [("active", "=", True)])

        self._reset_domain_configuration()
        with self.assertRaises(ValidationError):
            self.helpdesk_team.project_domain_python = "x +"

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain_python = "1/0"
        runtime_error_ticket = self._create_ticket_minimal(name="T_py_runtime_error")
        with self._mute_helpdesk_ticket_logger():
            self.assertEqual(runtime_error_ticket._get_project_domain(), [])

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain_python = "domain = 1"
        invalid_domain_type_ticket = self._create_ticket_minimal(
            name="T_py_invalid_type"
        )
        with self._mute_helpdesk_ticket_logger():
            self.assertEqual(invalid_domain_type_ticket._get_project_domain(), [])

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain_python = "raise Exception('Error Domain')"
        explicit_exception_ticket = self._create_ticket_minimal(name="T_py_exception")
        with self._mute_helpdesk_ticket_logger():
            self.assertEqual(explicit_exception_ticket._get_project_domain(), [])

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain_python = ""
        empty_python_ticket = self._create_ticket_minimal(name="T_empty_py")
        self.assertEqual(empty_python_ticket._get_project_domain(), [])

        exec_mode_ticket = self._create_ticket_minimal(name="T_run_python_exec_path")
        exec_mode_domain = exec_mode_ticket._run_python_domain(
            "42\n\ndomain = [('active', '=', True)]"
        )
        self.assertEqual(exec_mode_domain, [("active", "=", True)])

        empty_recordset_domain = (
            self.env["helpdesk.ticket"]
            .browse()
            ._run_python_domain("[('active', '=', True)]")
        )
        self.assertEqual(empty_recordset_domain, [("active", "=", True)])

    def test_task_domain_filters_and_domain_contains_field(self):
        self._reset_domain_configuration()
        selected_project = self.active_project
        matching_task = self.env["project.task"].create(
            {"name": "Task 1", "project_id": selected_project.id}
        )
        non_matching_task = self.env["project.task"].create(
            {"name": "Task 2", "project_id": self.inactive_project.id}
        )
        task_filter_ticket = self._create_ticket_minimal(
            name="T_task_filter", project_id=selected_project.id
        )
        task_domain = task_filter_ticket._get_task_domain()
        self.assertIn(("project_id", "=", selected_project.id), task_domain)
        available_tasks = self.env["project.task"].search(task_domain)
        self.assertIn(matching_task, available_tasks)
        self.assertNotIn(non_matching_task, available_tasks)

        self._reset_domain_configuration()
        self.helpdesk_team.task_domain_python = (
            "domain = [('project_id', '=', ticket.project_id.id)]"
        )
        no_duplicate_filter_ticket = self._create_ticket_minimal(
            name="T_task_no_dup", project_id=selected_project.id
        )
        normalized_task_domain = expression.normalize_domain(
            no_duplicate_filter_ticket._get_task_domain()
        )
        project_id_filters = [
            leaf
            for leaf in normalized_task_domain
            if isinstance(leaf, list | tuple)
            and len(leaf) == 3
            and leaf[0] == "project_id"
            and leaf[1] == "="
        ]
        self.assertEqual(len(project_id_filters), 1)

        recursive_domain = [
            "|",
            ("name", "=", "X"),
            [
                "&",
                ("active", "=", True),
                ("project_id", "=", self.active_project.id),
            ],
        ]
        self.assertTrue(
            no_duplicate_filter_ticket._domain_contains_field(
                recursive_domain, "project_id"
            )
        )
        self.assertFalse(
            no_duplicate_filter_ticket._domain_contains_field(False, "project_id")
        )
        self.assertFalse(
            no_duplicate_filter_ticket._domain_contains_field(
                "not a domain", "project_id"
            )
        )
        self.assertFalse(
            no_duplicate_filter_ticket._domain_contains_field(
                [("name", "=", "X")], "project_id"
            )
        )

        no_project_ticket = self._create_ticket_minimal(name="T_no_project_selected")
        no_project_domain = no_project_ticket._get_task_domain()
        self.assertIsInstance(no_project_domain, list)

    def test_views_onchange_compute_ids_and_create_multi_sanitization(self):
        self._reset_domain_configuration()
        self.helpdesk_team.project_domain = "[('active', '=', True)]"
        self.helpdesk_team.task_domain = (
            "[('project_id', '=', %d)]" % self.active_project.id
        )
        view_ticket = self._create_ticket_minimal(
            name="T_view", project_id=self.active_project.id
        )

        view_domain_calls = [
            ("_get_project_domain_for_view", {"active_id": view_ticket.id}),
            (
                "_get_project_domain_for_view",
                {"default_team_id": self.helpdesk_team.id},
            ),
            ("_get_project_domain_for_view", {}),
            ("_get_task_domain_for_view", {"active_id": view_ticket.id}),
            ("_get_task_domain_for_view", {"default_team_id": self.helpdesk_team.id}),
            ("_get_task_domain_for_view", {}),
        ]
        for method_name, context_values in view_domain_calls:
            with self.subTest(method=method_name, ctx=context_values):
                model = self.env["helpdesk.ticket"].with_context(**context_values)
                resolved_domain = getattr(model, method_name)()
                self.assertIsInstance(resolved_domain, list)

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain = "[('active', '=', True)]"
        onchange_project_ticket = self.env["helpdesk.ticket"].new(
            {
                "name": "T_onchange_proj",
                "description": "desc",
                "team_id": self.helpdesk_team.id,
                "project_id": self.inactive_project.id,
            }
        )
        onchange_project_result = onchange_project_ticket._onchange_project_domain()
        self.assertIsInstance(onchange_project_result, dict)
        self.assertFalse(onchange_project_ticket.project_id)
        self.assertFalse(onchange_project_ticket.task_id)
        self.assertIn("domain", onchange_project_result)
        self.assertIn("project_id", onchange_project_result["domain"])

        self._reset_domain_configuration()
        valid_project = self.active_project
        invalid_project = self.inactive_project
        invalid_task_for_project = self.env["project.task"].create(
            {"name": "Bad", "project_id": invalid_project.id}
        )
        self.helpdesk_team.task_domain = "[('project_id', '=', %d)]" % valid_project.id
        onchange_task_ticket = self.env["helpdesk.ticket"].new(
            {
                "name": "T_onchange_task",
                "description": "desc",
                "team_id": self.helpdesk_team.id,
                "project_id": valid_project.id,
                "task_id": invalid_task_for_project.id,
            }
        )
        onchange_task_result = onchange_task_ticket._onchange_task_domain()
        self.assertIsInstance(onchange_task_result, dict)
        self.assertFalse(onchange_task_ticket.task_id)
        self.assertIn("domain", onchange_task_result)
        self.assertIn("task_id", onchange_task_result["domain"])

        self._reset_domain_configuration()
        compute_all_ticket = self._create_ticket_minimal(name="T_compute_no_domain")
        self.assertTrue(hasattr(compute_all_ticket, "project_domain_ids"))
        self.assertTrue(hasattr(compute_all_ticket, "task_domain_ids"))
        self.assertIn(self.active_project, compute_all_ticket.project_domain_ids)

        self._reset_domain_configuration()
        self.helpdesk_team.project_domain = "[('id', '=', -1)]"
        self.company.helpdesk_mgmt_task_domain = "[('id', '=', -1)]"
        compute_none_ticket = self._create_ticket_minimal(
            name="T_compute_domain_matches_none", project_id=self.active_project.id
        )
        self.assertEqual(len(compute_none_ticket.project_domain_ids), 0)
        self.assertEqual(len(compute_none_ticket.task_domain_ids), 0)

        self._reset_domain_configuration()
        valid_task = self.env["project.task"].create(
            {"name": "Good", "project_id": valid_project.id}
        )
        invalid_task = self.env["project.task"].create(
            {"name": "Bad2", "project_id": invalid_project.id}
        )
        self.helpdesk_team.project_domain = "[('active', '=', True)]"
        self.helpdesk_team.task_domain = "[('project_id','=',%d)]" % valid_project.id

        created_tickets = self.env["helpdesk.ticket"].create(
            [
                {
                    "name": "T_multi_1",
                    "description": "desc",
                    "team_id": self.helpdesk_team.id,
                    "project_id": str(valid_project.id),
                    "task_id": str(valid_task.id),
                },
                {
                    "name": "T_multi_2",
                    "description": "desc",
                    "team_id": self.helpdesk_team.id,
                    "project_id": str(valid_project.id),
                    "task_id": str(invalid_task.id),
                },
                {
                    "name": "T_multi_3",
                    "description": "desc",
                    "team_id": self.helpdesk_team.id,
                    "project_id": str(invalid_project.id),
                    "task_id": str(valid_task.id),
                },
            ]
        )

        self.assertEqual(len(created_tickets), 3)

        first_ticket, second_ticket, third_ticket = (
            created_tickets[0],
            created_tickets[1],
            created_tickets[2],
        )

        self.assertEqual(first_ticket.project_id, valid_project)
        self.assertEqual(first_ticket.task_id, valid_task)

        self.assertEqual(second_ticket.project_id, valid_project)
        self.assertFalse(second_ticket.task_id)

        self.assertFalse(third_ticket.project_id)
        self.assertFalse(third_ticket.task_id)
