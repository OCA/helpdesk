# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestHelpdeskMgmtProjectStage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket_stage_progress = cls.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )
        cls.ticket_stage_done = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.task_stage_progress = cls.env["project.task.type"].create(
            {
                "name": "stage in progress",
                "ticket_stage_ids": [Command.link(cls.ticket_stage_progress.id)],
            }
        )
        cls.task_stage_done = cls.env["project.task.type"].create(
            {
                "name": "stage done",
                "ticket_stage_ids": [Command.link(cls.ticket_stage_done.id)],
            }
        )
        cls.ticket_stage_progress.task_stage_ids = [
            Command.link(cls.task_stage_progress.id)
        ]
        cls.ticket_stage_done.task_stage_ids = [Command.link(cls.task_stage_done.id)]
        cls.project = cls.env["project.project"].create(
            {
                "name": "Helpdesk project",
                "type_ids": [
                    Command.set((cls.task_stage_progress + cls.task_stage_done).ids)
                ],
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Ticket task 1",
                "project_id": cls.project.id,
                "stage_id": cls.task_stage_progress.id,
            }
        )
        cls.task_2 = cls.env["project.task"].create(
            {
                "name": "Ticket task 2",
                "project_id": cls.project.id,
                "stage_id": cls.task_stage_progress.id,
            }
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Ticket",
                "project_id": cls.project.id,
                "description": "Change stage",
                "stage_id": cls.ticket_stage_progress.id,
            }
        )
        cls.user = cls.env.ref("base.user_demo")

    def test_task_sync(self):
        """Test that configured stages stay in sync"""
        ticket = self.ticket.with_user(self.user)
        task = self.task.with_user(self.user)
        task.stage_id = self.task_stage_progress
        ticket.task_id = task
        task.stage_id = self.task_stage_done
        self.assertEqual(ticket.stage_id, self.ticket_stage_done)
        ticket.stage_id = self.ticket_stage_done
        self.assertEqual(task.stage_id, self.task_stage_done)
        ticket.stage_id = self.ticket_stage_progress
        self.assertEqual(task.stage_id, self.task_stage_progress)
        task.stage_id = False
        self.assertEqual(ticket.stage_id, self.ticket_stage_progress)

    def test_sync_limit_single_task_active_with_multiple_tasks(self):
        """
        Test limitation: If Ticket has 2 tasks and restriction is ON,
        moving ONE task should NOT move the ticket.
        """
        self.ticket_stage_progress.sync_limit_single_task = True
        self.task.write({"ticket_ids": [Command.link(self.ticket.id)]})
        self.task_2.write({"ticket_ids": [Command.link(self.ticket.id)]})
        self.task.stage_id = self.task_stage_done
        self.assertEqual(self.ticket.stage_id, self.ticket_stage_progress)

    def test_sync_limit_single_task_active_with_one_task(self):
        """
        Test limitation: If Ticket has only 1 task and restriction is ON,
        moving the task SHOULD move the ticket normally.
        """
        self.ticket_stage_progress.sync_limit_single_task = True
        self.task.write({"ticket_ids": [Command.link(self.ticket.id)]})
        self.task_2.write({"ticket_ids": [Command.clear()]})
        self.task.stage_id = self.task_stage_done
        self.assertEqual(self.ticket.stage_id, self.ticket_stage_done)

    def test_sync_limit_loop_continue(self):
        """
        Test strict coverage of the 'continue' statement.
        We configure one Task linked to TWO tickets:
        1. Ticket A (Original): Has multiple tasks -> Should SKIP (hit continue)
        2. Ticket B (New): Has single task -> Should UPDATE (prove loop continued)
        """
        self.ticket_stage_progress.sync_limit_single_task = True

        ticket_b = self.ticket.copy({"name": "Ticket B"})

        self.task.write({"ticket_ids": [Command.link(self.ticket.id)]})
        self.task_2.write({"ticket_ids": [Command.link(self.ticket.id)]})
        self.task.write({"ticket_ids": [Command.link(ticket_b.id)]})
        self.task.stage_id = self.task_stage_done

        self.assertEqual(self.ticket.stage_id, self.ticket_stage_progress)
        self.assertEqual(ticket_b.stage_id, self.ticket_stage_done)
