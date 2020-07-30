import time

from odoo.tests import tagged

from .common import TestHelpdeskTicketBase


class TestHelpdeskTicket(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket = cls.ticket_a_unassigned

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
        self.ticket.write({"user_id": self.user.id})
        self.assertTrue(
            self.ticket.assigned_date,
            "Helpdesk Ticket: An assigned ticket " "should contain a assigned_date.",
        )

    def test_helpdesk_ticket_number(self):
        self.assertNotEqual(
            self.ticket.number,
            "/",
            "Helpdesk Ticket: A ticket should have " "a number.",
        )
        ticket_number_1 = int(self.ticket._prepare_ticket_number(values={})[2:])
        ticket_number_2 = int(self.ticket._prepare_ticket_number(values={})[2:])
        self.assertEqual(ticket_number_1 + 1, ticket_number_2)

    def test_helpdesk_ticket_copy(self):
        old_ticket_number = self.ticket.number
        copy_ticket_number = self.ticket.copy().number
        self.assertTrue(
            copy_ticket_number != "/" and old_ticket_number != copy_ticket_number,
            "Helpdesk Ticket: A new ticket can not "
            "have the same number than the origin ticket.",
        )

    def test_helpdesk_ticket_message_new(self):
        Partner = self.env["res.partner"]
        Ticket = self.env["helpdesk.ticket"]

        newPartner = Partner.create(
            {
                "name": "Jill",
                "email": "jill@example.com",
            }
        )
        title = "Test Helpdesk ticket message new"
        msg_id = "0000000000007c50e905cf5b1f2a@example.com"
        msg_dict = {
            "message_id": msg_id,
            "subject": title,
            "email_from": "Bob <bob@example.com>",
            "to": "jill@example.com",
            "cc": "sally@example.com",
            "recipients": "jill@example.com+sally@example.com",
            "partner_ids": [newPartner.id],
            "body": "This the body",
            "date": "2021-10-10",
        }
        try:
            t = Ticket.message_new(msg_dict)
        except Exception as error:
            self.fail("%s: %s" % (type(error), error))
        self.assertEqual(t.name, title, "The ticket should have the correct title.")

        title = "New title"
        update_vals = {"name": title}
        try:
            t.message_update(msg_dict, update_vals)
        except Exception as error:
            self.fail("%s: %s" % (type(error), error))
        self.assertEqual(
            t.name, title, "The ticket should have the correct (new) title."
        )

    def test_helpdesk_ticket_multiple(self):
        Ticket = self.env["helpdesk.ticket"]
        Partner = self.env["res.partner"]

        partner_1 = Partner.create({"name": "Partner 1", "email": "partner1@test.com"})
        partner_2 = Partner.create({"name": "Partner 2", "email": "partner2@test.com"})
        tickets = Ticket.create(
            [
                {
                    "name": "Test 1",
                    "description": "Ticket test number 1",
                    "user_id": self.user.id,
                    "partner_id": partner_1.id,
                },
                {
                    "name": "Test 2",
                    "description": "Ticket test number 2",
                    "user_id": self.user_demo.id,
                    "partner_id": partner_2.id,
                },
            ]
        )
        self.assertEqual(len(tickets), 2)

    def test_helpdesk_ticket_access(self):
        Ticket = self.env["helpdesk.ticket"]

        t = Ticket.create(
            {
                "name": "Test 1",
                "description": "Ticket test",
            }
        )
        self.assertEqual(t.access_url, "/my/ticket/%s" % t.id)
        t.partner_id = self.user_portal.partner_id.id
        self.assertTrue(t.partner_can_access())


@tagged("post_install", "-at_install")
class TestHelpdeskTicketPostInstall(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_helpdesk_ticket_assign_notify(self):
        Ticket = self.env["helpdesk.ticket"]
        Message = self.env["mail.message"]

        t = Ticket.create(
            {
                "name": "Test 1",
                "description": "Ticket test",
            }
        )
        t.user_id = self.user_demo.id
        m = Message.search(
            [
                ("model", "=", "helpdesk.ticket"),
                ("res_id", "=", t.id),
                ("message_type", "=", "user_notification"),
            ]
        )
        self.assertTrue(
            "You have been assigned to the Helpdesk Ticket %s" % t.display_name
            in m.body
        )
        self.assertTrue("res_id=%s" % t.id in m.body)
