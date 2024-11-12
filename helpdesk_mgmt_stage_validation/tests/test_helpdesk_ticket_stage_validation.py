# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestHelpdeskStageValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.stage = cls.env["helpdesk.ticket.stage"]
        cls.helpdesk_ticket = cls.env["helpdesk.ticket"]
        cls.ir_model_fields = cls.env["ir.model.fields"]
        # Get some fields to use in the stages
        cls.ticket_field = cls.ir_model_fields.search(
            [("model", "=", "helpdesk.ticket"), ("name", "=", "assigned_date")]
        )
        cls.stage_ticket_default = cls.stage.create(
            {
                "name": "Helpdesk Ticket Stage Default",
            }
        )
        cls.stage_ticket_assigned = cls.stage.create(
            {
                "name": "Helpdesk Ticket Assigned",
                "validate_field_ids": [(6, 0, [cls.ticket_field.id])],
            }
        )
        cls.ticket = cls.helpdesk_ticket.create(
            {
                "name": "Helpdesk Ticket",
                "description": "Helpdesk Ticket Description",
                "stage_id": cls.stage_ticket_default.id,
            }
        )

    def get_validate_message(self, ticket, stage):
        validate_message = False
        field_ids = stage.validate_field_ids
        field_names = [x.name for x in field_ids]
        values = ticket.read(field_names)
        fields = [
            field.field_description for field in field_ids if not values[0][field.name]
        ]
        fields = ", ".join(fields)
        if fields:
            validate_message = (
                f"Ticket {ticket.name} can't be moved to the stage "
                f"{stage.name} until the following fields are set: {fields}."
            )
        return validate_message

    def test_helpdesk_ticket_stage_validation(self):
        validate_message = self.get_validate_message(
            self.ticket, self.stage_ticket_assigned
        )
        with self.assertRaisesRegex(ValidationError, validate_message):
            self.ticket.write({"stage_id": self.stage_ticket_assigned.id})
        self.ticket.write({"assigned_date": fields.datetime.now()})
        self.ticket.write({"stage_id": self.stage_ticket_assigned.id})
        self.assertEqual(self.ticket.stage_id, self.stage_ticket_assigned)
