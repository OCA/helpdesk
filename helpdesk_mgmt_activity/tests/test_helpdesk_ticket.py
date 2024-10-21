# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Date
from odoo.tests import Form

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskTicket(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"]._get("res.partner")
        cls.test_partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.activity_type_meeting = cls.env.ref("mail.mail_activity_data_meeting")
        cls.env["ir.config_parameter"].sudo().set_param(
            "helpdesk_mgmt_activity.helpdesk_available_model_ids", cls.partner_model.ids
        )

        # Stages
        cls.progress_stage = cls.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )
        cls.awaiting_stage = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_awaiting")

    def create_ticket_and_activity(self):
        """Create ticket and activity for record"""
        ticket = self._create_ticket(self.team_a, self.user)
        ticket.write(
            {
                "record_ref": f"res.partner,{self.test_partner.id}",
                "source_activity_type_id": self.activity_type_meeting.id,
                "date_deadline": Date.today(),
            }
        )
        action = ticket.perform_action()
        activity = ticket.record_ref.with_context(
            **action.get("context", {})
        ).activity_schedule(
            summary=ticket.name,
            note=ticket.description,
            date_deadline=ticket.date_deadline,
        )
        return ticket, activity

    def test_ticket_next_stage(self):
        """Test flow check stage for ticket"""
        # Set team config
        self.team_a.write(
            {
                "allow_set_activity": True,
                "activity_stage_id": self.stage_closed.id,
            }
        )
        # Create ticket
        ticket = self._create_ticket(self.team_a, self.user)

        self.assertEqual(ticket.stage_id, self.new_stage)
        self.assertEqual(ticket.next_stage_id, self.progress_stage)

        # Set activity configuration for ticket
        ticket.write(
            {
                "record_ref": f"res.partner,{self.test_partner.id}",
                "source_activity_type_id": self.activity_type_meeting.id,
                "date_deadline": Date.today(),
            }
        )

        # Create activity for source record
        action = ticket.perform_action()
        activity = ticket.record_ref.with_context(
            **action.get("context", {})
        ).activity_schedule(
            summary=ticket.name,
            note=ticket.description,
            date_deadline=ticket.date_deadline,
        )

        self.assertEqual(ticket.stage_id, self.progress_stage)

        # Activity set done
        activity.action_done()

        self.assertEqual(ticket.stage_id, self.stage_closed)

    def test_ticket_available_model_ids(self):
        """Test flow when available model for ticket is updated"""
        settings = self.env["res.config.settings"].create({})
        with Form(settings) as form:
            form.helpdesk_available_model_ids.add(self.partner_model)
        values = settings.get_values()
        self.assertEqual(
            values.get("helpdesk_available_model_ids"), self.partner_model.ids
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "helpdesk_mgmt_activity.helpdesk_available_model_ids", False
        )
        values = settings.get_values()
        self.assertFalse(values.get("helpdesk_available_model_ids"))

    def test_ticket_record_ref(self):
        """Test flow when change source record"""
        ticket = self._create_ticket(self.team_a, self.user)
        self.assertFalse(ticket.record_ref)
        self.assertFalse(ticket.res_model)
        self.assertFalse(ticket.res_id)

        ticket.record_ref = f"res.partner,{self.test_partner.id}"
        self.assertEqual(ticket.record_ref, self.test_partner)
        self.assertEqual(ticket.res_id, self.test_partner.id)
        self.assertEqual(ticket.res_model, "res.partner")

        ticket.record_ref = False
        self.assertFalse(ticket.res_id)
        self.assertFalse(ticket.res_model)

    def test_perform_action(self):
        """Test flow when create action in record reference"""
        ticket = self._create_ticket(self.team_a, self.user)

        with self.assertRaises(UserError) as error:
            ticket.perform_action()
        self.assertEqual(error.exception.args[0], "You cannot create activity!")

        ticket.team_id.allow_set_activity = True

        with self.assertRaises(UserError) as error:
            ticket.perform_action()
        self.assertEqual(error.exception.args[0], "Source Record is not set!")

        ticket.record_ref = f"res.partner,{self.test_partner.id}"

        with self.assertRaises(UserError) as error:
            ticket.perform_action()
        self.assertEqual(error.exception.args[0], "Activity Type is not set!")

        ticket.source_activity_type_id = self.activity_type_meeting
        ticket.date_deadline = False

        with self.assertRaises(UserError) as error:
            ticket.perform_action()
        self.assertEqual(error.exception.args[0], "Date Deadline is not set!")

        ticket.date_deadline = Date.today()

        action = ticket.perform_action()

        self.assertDictEqual(
            action,
            {
                "type": "ir.actions.act_window",
                "name": "Helpdesk Ticket Action",
                "view_mode": "form",
                "res_model": "mail.activity",
                "view_type": "form",
                "context": {
                    "default_res_model_id": self.partner_model.id,
                    "default_res_id": ticket.res_id,
                    "default_activity_type_id": ticket.source_activity_type_id.id,
                    "default_date_deadline": ticket.date_deadline,
                    "default_ticket_id": ticket.id,
                    "default_summary": ticket.name,
                    "default_user_id": ticket.user_id.id,
                },
                "target": "new",
            },
        )

    def test_helpdesk_activity_with_team_stage(self):
        """
        Test flow when create activity from helpdesk ticket
        and done it. Ticket is moved to cancel stage
        """
        self.team_a.write(
            {
                "allow_set_activity": True,
                "activity_stage_id": self.stage_closed.id,
            }
        )
        ticket, activity = self.create_ticket_and_activity()
        self.assertEqual(
            activity.res_model_id.id, self.partner_model.id, "Model id's must be equal"
        )
        self.assertEqual(
            activity.res_id,
            self.test_partner.id,
            "Res ID must be equal to test partner ID",
        )

        activity.action_done()
        self.assertEqual(
            ticket.stage_id.id, self.stage_closed.id, "Stage ID must be equal"
        )

    def test_helpdesk_activity_without_team_stage(self):
        """
        Test flow when create activity from helpdesk ticket
        and done it without activity_stage_id field value from ticket team
        """
        self.team_a.allow_set_activity = True
        ticket, activity = self.create_ticket_and_activity()
        ticket_stage_id = ticket.stage_id.id
        self.assertEqual(
            activity.res_model_id.id, self.partner_model.id, "Model id's must be equal"
        )
        self.assertEqual(
            activity.res_id,
            self.test_partner.id,
            "Res ID must be equal to test partner ID",
        )

        activity.action_done()
        self.assertEqual(ticket_stage_id, ticket.stage_id.id, "Stage ID must be equal")
