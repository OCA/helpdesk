import re
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

        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
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

    def test_helpdesk_assign_msg(self):

        count = len(self.ticket.message_ids)
        self.ticket.user_id = self.env.user

        self.assertEqual(
            len(self.ticket.message_ids),
            count + 1,
            "Number of msgs in chatter should increase",
        )
        assignRegex = "The ticket HT[0-9]+ has been assigned to you."
        self.assertNotEqual(
            re.search(assignRegex, self.ticket.message_ids.sorted("id")[-1].body),
            None,
            "The content should match a line of the assignment email.",
        )

    def test_helpdesk_new_from_email(self):

        # The only part of new email reception we want to test is message_new()
        msg = {
            "message_id": "431858539581299-openerp-400-helpdesk.ticket@example.org",
            "subject": "subject",
            "email_from": "from@example.org",
            "to": "to@example.org",
            "recipients": "to@example.org",
            "author_id": self.env.ref("base.res_partner_1").id,
            "body": "unified_body",
            "is_internal": False,
            "date": "2021-11-01 00:00:00",
        }
        tkt = self.env["helpdesk.ticket"].message_new(msg)

        self.assertEqual(
            tkt.partner_id,
            self.env.ref("base.res_partner_1"),
            "The ticket has a partner",
        )
        self.assertEqual(
            tkt.partner_name,
            self.env.ref("base.res_partner_1").name,
            "The ticket has a Partner Name",
        )
        self.assertEqual(
            tkt.partner_email,
            self.env.ref("base.res_partner_1").email,
            "The ticket has a Partner Email",
        )
        self.assertEqual(
            tkt.channel_id,
            self.env.ref("helpdesk_mgmt.helpdesk_ticket_channel_email"),
            "The ticket 'Channel' should be 'Email'",
        )
        found = False
        newRegex = "Thank you for reaching out to us"
        for msg in tkt.message_ids:
            res = re.search(newRegex, msg.body)
            if res is not None:
                found = True
        if not found:
            self.fail("The content should match part of the acknowledgement email.")
