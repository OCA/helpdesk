# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class HelpdeskTicketStageServerAction(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(HelpdeskTicketStageServerAction, cls).setUpClass()
        cls.ServerAction = cls.env["ir.actions.server"]
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]
        cls.HelpdeskTicketStage = cls.env["helpdesk.ticket.stage"]
        cls.field = cls.env["ir.model.fields"]._get(cls.HelpdeskTicket._name, "user_id")
        cls.server_action_helpdesk_ticket = cls.ServerAction.create(
            {
                "name": "Helpdesk Ticket Server Action",
                "model_id": cls.env.ref("helpdesk_mgmt.model_helpdesk_ticket").id,
                "state": "object_write",
                "fields_lines": [
                    (
                        0,
                        0,
                        {
                            "col1": cls.field.id,
                            "evaluation_type": "value",
                            "value": cls.env.user.id,
                        },
                    )
                ],
            }
        )
        cls.helpdesk_ticket_stage_1 = cls.HelpdeskTicketStage.create(
            {"name": "Stage 1", "sequence": 1}
        )
        cls.helpdesk_ticket_stage_2 = cls.HelpdeskTicketStage.create(
            {
                "name": "Stage 2",
                "action_id": cls.server_action_helpdesk_ticket.id,
                "sequence": 2,
            }
        )

    def test_helpdesk_ticket_create(self):
        self.helpdesk_ticket_1 = self.HelpdeskTicket.create(
            {
                "name": "Helpdesk Ticket 1",
                "stage_id": self.helpdesk_ticket_stage_2.id,
                "description": "Helpdesk Ticket Description",
            }
        )
        self.assertEqual(self.helpdesk_ticket_1.user_id, self.env.user)

    def test_helpdesk_ticket_write(self):
        self.helpdesk_ticket_2 = self.HelpdeskTicket.create(
            {
                "name": "Helpdesk Ticket 2",
                "stage_id": self.helpdesk_ticket_stage_1.id,
                "description": "Helpdesk Ticket Description",
            }
        )
        self.helpdesk_ticket_3 = self.HelpdeskTicket.create(
            {
                "name": "Helpdesk Ticket 3",
                "stage_id": self.helpdesk_ticket_stage_1.id,
                "description": "Helpdesk Ticket Description",
            }
        )
        self.assertNotEqual(self.helpdesk_ticket_2.user_id, self.env.user)
        self.assertNotEqual(self.helpdesk_ticket_3.user_id, self.env.user)
        self.helpdesk_ticket_2.write({"stage_id": self.helpdesk_ticket_stage_2.id})
        self.helpdesk_ticket_3.write({"stage_id": self.helpdesk_ticket_stage_2.id})
        self.assertEqual(self.helpdesk_ticket_2.user_id, self.env.user)
        self.assertEqual(self.helpdesk_ticket_3.user_id, self.env.user)
        self.helpdesk_ticket_3.write({"user_id": False})
        self.helpdesk_ticket_3.write({"stage_id": self.helpdesk_ticket_stage_2.id})
        self.assertFalse(self.helpdesk_ticket_3.user_id)

    def test_helpdesk_ticket_without_stage(self):
        self.helpdesk_ticket_4 = self.HelpdeskTicket.create(
            {
                "name": "Helpdesk Ticket 4",
                "description": "Helpdesk Ticket Description",
            }
        )
        self.assertFalse(self.helpdesk_ticket_4.user_id)
        self.helpdesk_ticket_stage_3 = self.HelpdeskTicketStage.create(
            {
                "name": "Stage 3",
                "sequence": 3,
            }
        )
        self.helpdesk_ticket_4.write({"stage_id": self.helpdesk_ticket_stage_3.id})
        self.assertFalse(self.helpdesk_ticket_4.user_id)
        self.helpdesk_ticket_4.write({"stage_id": self.helpdesk_ticket_stage_2.id})
        self.assertEqual(self.helpdesk_ticket_4.user_id, self.env.user)
