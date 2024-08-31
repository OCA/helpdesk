import time

from odoo.addons.test_mail.tests.test_mail_gateway import MAIL_TEMPLATE

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

    def test_ticket_with_team_stage(self):
        self.new_stage.team_ids = [(6, 0, [self.team_a.id, self.team_b.id])]
        in_progress_stage = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )
        in_progress_stage.team_ids = [(6, 0, [self.team_b.id])]
        new_ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "New Ticket",
                "description": "Description",
                "team_id": self.team_a.id,
                "user_id": self.user.id,
                "priority": "1",
            }
        )
        self.assertEqual(new_ticket.stage_id, self.new_stage)
        self.new_stage.team_ids = [(6, 0, [self.team_a.id])]
        new_ticket.team_id = self.team_b
        self.assertEqual(new_ticket.stage_id, in_progress_stage)
        self.new_stage.team_ids = False
        new_ticket.team_id = False
        self.assertEqual(new_ticket.stage_id, self.new_stage)

    def test_ticket_without_team(self):
        new_ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "New Ticket",
                "description": "Description",
                "user_id": self.user.id,
                "priority": "1",
            }
        )
        self.assertEqual(self.new_stage, new_ticket.stage_id)

    def test_create_ticket_with_mail_template(self):
        new_stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        new_stage.team_ids = [(6, 0, [self.team_a.id])]
        new_stage.mail_template_id = self.env.ref(
            "helpdesk_mgmt.closed_ticket_template"
        )
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "I'm a robot, hello",
                "team_id": self.team_a.id,
                "stage_id": new_stage.id,
                "description": "Description",
            }
        )
        ticket_good_reception = ticket.message_ids.filtered(
            lambda m: m.message_type == "email"
        )
        self.assertIn("closed", ticket_good_reception.subject)

    def test_create_ticket_from_alias_mail(self):
        server = self.env["fetchmail.server"].create(
            {
                "name": "Demo server",
                "server_type": "pop",
                "server": "pop3.example.com",
            }
        )
        self.env["mail.alias"].create(
            {
                "alias_name": "team_a_alias",
                "alias_model_id": self.env.ref(
                    "helpdesk_mgmt.model_helpdesk_ticket"
                ).id,
                "alias_contact": "everyone",
                "alias_defaults": {"team_id": self.team_a.id},
                "alias_parent_model_id": self.env.ref(
                    "helpdesk_mgmt.model_helpdesk_ticket_team"
                ).id,
            }
        )
        new_stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        new_stage.team_ids = [(6, 0, [self.team_a.id])]
        new_stage.mail_template_id = self.env.ref(
            "helpdesk_mgmt.closed_ticket_template"
        )
        email = "from@me.com"

        self.env["mail.thread"].with_context(
            default_fetchmail_server_id=server.id
        ).message_process(
            server.object_id.model,
            MAIL_TEMPLATE.format(
                return_path=email,
                email_from=email,
                to="team_a_alias@example.com",
                cc="team_aa_alias@example.com",
                subject="Hello Ticket",
                extra="",
                msg_id="<test@example.com>",
            ),
        )

        ticket = self.env["helpdesk.ticket"].search([("name", "=", "Hello Ticket")])
        self.assertEqual(len(ticket.message_ids), 2)
        ticket_good_reception = ticket.message_ids.filtered(
            lambda m: m.message_type == "email" and m.email_from != email
        )
        self.assertEqual(len(ticket_good_reception), 1)
        self.assertIn("closed", ticket_good_reception.subject)
