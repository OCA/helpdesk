import datetime
import time

from odoo.tests import common


class TestHelpdeskTicket(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        cls.user_admin = cls.env.ref("base.user_root")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.stage_new = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
        )

        cls.auto_start_time: datetime.datetime = (
            datetime.datetime.now() - datetime.timedelta(hours=2)
        )
        cls.ticket_auto_stage = helpdesk_ticket.create(
            {
                "name": "Test 2",
                "description": "Ticket test 2",
                "auto_last_update": cls.auto_start_time,
            }
        )

    def test_helpdesk_ticket_datetimes(self):
        old_stage_update = self.ticket.last_stage_update

        self.assertTrue(
            self.ticket.last_stage_update,
            "Helpdesk Ticket: Helpdesk ticket should "
            "have a last_stage_update at all times.",
        )

        self.assertFalse(
            self.ticket.closed_date,
            "Helpdesk Ticket: No closed date "
            "should be set for a non closed "
            "ticket.",
        )

        time.sleep(1)

        self.ticket.write({"stage_id": self.stage_closed.id})

        self.assertTrue(
            self.ticket.closed_date,
            "Helpdesk Ticket: A closed ticket " "should have a closed_date value.",
        )
        self.assertTrue(
            old_stage_update < self.ticket.last_stage_update,
            "Helpdesk Ticket: The last_stage_update "
            "should be updated at every stage_id "
            "change.",
        )

        self.ticket.write({"user_id": self.user_admin.id})
        self.assertTrue(
            self.ticket.assigned_date,
            "Helpdesk Ticket: An assigned ticket " "should contain a assigned_date.",
        )

    def test_helpdesk_ticket_number(self):
        self.assertNotEquals(
            self.ticket.number,
            "/",
            "Helpdesk Ticket: A ticket should have " "a number.",
        )

    def test_helpdesk_ticket_copy(self):
        old_ticket_number = self.ticket.number

        copy_ticket_number = self.ticket.copy().number

        self.assertTrue(
            copy_ticket_number != "/" and old_ticket_number != copy_ticket_number,
            "Helpdesk Ticket: A new ticket can not "
            "have the same number than the origin ticket.",
        )

    def test_automatic_stage(self):
        self.stage_new.write(
            {
                "auto_next_number": 1,
                "auto_next_type": "hour",
                "auto_next_stage_id": self.stage_closed.id,
            }
        )

        self.assertEqual(self.stage_new.auto_next_number, 1)
        self.assertEqual(self.stage_new.auto_next_type, "hour")
        self.assertEqual(self.stage_new.auto_next_stage_id.id, self.stage_closed.id)
        self.assertEqual(self.ticket_auto_stage.auto_last_update, self.auto_start_time)
        self.env[self.stage_new._name].change_stage()
        self.assertEqual(self.ticket_auto_stage.stage_id.id, self.stage_closed.id)
