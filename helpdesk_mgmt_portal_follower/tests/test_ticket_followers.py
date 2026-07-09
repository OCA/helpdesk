from odoo import http

from odoo.addons.base.tests.common import HttpCaseWithUserPortal


class TestSubmitPortalTicketBase(HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.new_ticket_title = "Test title"
        cls.new_ticket_description = ("This is a test",)
        cls.category = cls.env["helpdesk.ticket.category"].create({"name": "test"})
        cls.company = cls.env.ref("base.main_company")

        cls.follower_emails = "test1@testing.com, test2@testing.com"
        cls.partner_model = cls.env["res.partner"]
        cls.helpdesk_ticket_model = cls.env["helpdesk.ticket"]

        cls.partner_portal.parent_id = cls.company.partner_id

    def _submit_ticket_with_followers(self, response_code, **values):
        data = {
            "category": self.category.id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": self.new_ticket_description,
            "followers": self.follower_emails,
        }
        data.update(**values)
        resp = self.url_open("/submitted/ticket", data=data)
        self.assertEqual(resp.status_code, response_code)
        return resp

    def _submit_ticket_without_followers(self, response_code, **values):
        data = {
            "category": self.category.id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": self.new_ticket_description,
            "followers": "",
        }
        data.update(**values)
        resp = self.url_open("/submitted/ticket", data=data)
        self.assertEqual(resp.status_code, response_code)
        return resp

    def _submit_ticket(self, followers="", response_code=200, **values):
        data = {
            "category": self.category.id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": self.new_ticket_description,
            "followers": followers,
        }
        data.update(values)

        response = self.url_open("/submitted/ticket", data=data)

        self.assertEqual(response.status_code, response_code)

        return response

    def _get_created_ticket(self):
        return self.helpdesk_ticket_model.search(
            [("name", "=", self.new_ticket_title)],
            limit=1,
        )

    def _assert_followers(self, ticket, emails):
        for email in emails:
            partner = self.partner_model.search(
                [("email", "=ilike", email)],
            )

            self.assertEqual(
                len(partner),
                1,
                f"Expected exactly one partner for {email}",
            )
            self.assertIn(
                partner.id,
                ticket.message_partner_ids.ids,
                f"{email} is not subscribed to the ticket",
            )


class TestSubmitPortalTicket(TestSubmitPortalTicketBase):
    def test_submit_ticket_with_followers(self):
        self.authenticate("portal", "portal")
        self._submit_ticket_with_followers(response_code=200)

        ticket = self.helpdesk_ticket_model.search(
            [("name", "=", self.new_ticket_title)]
        )

        for email in self.follower_emails.split(","):
            partner = self.partner_model.search([("email", "=", email.strip())])
            self.assertEqual(len(partner), 1)
            self.assertIn(partner.id, ticket.message_partner_ids.ids)

    def test_submit_ticket_without_followers(self):
        self.authenticate("portal", "portal")
        self._submit_ticket_without_followers(response_code=200)

        ticket = self.helpdesk_ticket_model.search(
            [("name", "=", self.new_ticket_title)]
        )

        for email in self.follower_emails.split(","):
            partner = self.partner_model.search([("email", "=", email.strip())])
            self.assertEqual(len(partner), 0)
            self.assertNotIn(partner.id, ticket.message_partner_ids.ids)

    def test_submit_ticket_with_comma_separated_followers(self):
        self.authenticate("portal", "portal")

        emails = [
            "test1@testing.com",
            "test2@testing.com",
        ]

        self._submit_ticket(
            followers=", ".join(emails),
        )

        ticket = self._get_created_ticket()

        self._assert_followers(ticket, emails)

    def test_submit_ticket_with_semicolon_separated_followers(self):
        self.authenticate("portal", "portal")

        emails = [
            "test1@testing.com",
            "test2@testing.com",
        ]

        self._submit_ticket(
            followers="; ".join(emails),
        )

        ticket = self._get_created_ticket()

        self._assert_followers(ticket, emails)

    def test_submit_ticket_with_space_separated_followers(self):
        self.authenticate("portal", "portal")

        emails = [
            "test1@testing.com",
            "test2@testing.com",
        ]

        self._submit_ticket(
            followers=" ".join(emails),
        )

        ticket = self._get_created_ticket()

        self._assert_followers(ticket, emails)

    def test_submit_ticket_with_newline_separated_followers(self):
        self.authenticate("portal", "portal")

        emails = [
            "test1@testing.com",
            "test2@testing.com",
        ]

        self._submit_ticket(
            followers="\n".join(emails),
        )

        ticket = self._get_created_ticket()

        self._assert_followers(ticket, emails)

    def test_submit_ticket_with_mixed_separators(self):
        self.authenticate("portal", "portal")

        emails = [
            "test1@testing.com",
            "test2@testing.com",
            "test3@testing.com",
            "test4@testing.com",
        ]

        self._submit_ticket(
            followers=(
                "test1@testing.com, "
                "test2@testing.com; "
                "test3@testing.com "
                "test4@testing.com"
            ),
        )

        ticket = self._get_created_ticket()

        self._assert_followers(ticket, emails)

    def test_submit_ticket_with_duplicate_followers(self):
        self.authenticate("portal", "portal")

        email = "test1@testing.com"

        self._submit_ticket(
            followers=("test1@testing.com, " "test1@testing.com; " "test1@testing.com"),
        )

        ticket = self._get_created_ticket()

        partner = self.partner_model.search(
            [("email", "=ilike", email)],
        )

        self.assertEqual(len(partner), 1)
        self.assertIn(
            partner.id,
            ticket.message_partner_ids.ids,
        )

    def test_submit_ticket_reuses_existing_partner(self):
        self.authenticate("portal", "portal")

        existing_partner = self.partner_model.create(
            {
                "name": "Existing follower",
                "email": "existing@testing.com",
            }
        )

        self._submit_ticket(
            followers="existing@testing.com",
        )

        ticket = self._get_created_ticket()

        partners = self.partner_model.search(
            [
                ("email", "=ilike", "existing@testing.com"),
            ]
        )

        self.assertEqual(len(partners), 1)
        self.assertEqual(partners, existing_partner)
        self.assertIn(
            existing_partner.id,
            ticket.message_partner_ids.ids,
        )
