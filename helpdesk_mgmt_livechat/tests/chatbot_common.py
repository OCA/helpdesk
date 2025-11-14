# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.im_livechat.tests.chatbot_common import ChatbotCase
from odoo.addons.mail.tests.common import mail_new_test_user


class HelpdeskChatbotCase(ChatbotCase):
    @classmethod
    def setUpClass(cls):
        super(HelpdeskChatbotCase, cls).setUpClass()

        cls.company_id = cls.env["res.company"].create(
            {
                "name": "Test Company",
                "country_id": cls.env.ref("base.be").id,
            }
        )

        cls.user_public = mail_new_test_user(
            cls.env, login="user_public", groups="base.group_public", name="Public User"
        )
        cls.user_portal = mail_new_test_user(
            cls.env,
            login="user_portal",
            groups="base.group_portal",
            name="Portal User",
            company_id=cls.company_id.id,
            email="portal@example.com",
        )
        # update company_id on partner since the user's company is not propagated
        cls.user_portal.partner_id.write({"company_id": cls.company_id.id})

        cls.helpdesk_team = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Test Helpdesk Team 1",
                "company_id": cls.company_id.id,
            }
        )

        cls.step_dispatch_create_ticket = (
            cls.env["chatbot.script.answer"]
            .sudo()
            .create(
                {
                    "name": "Create a ticket",
                    "script_step_id": cls.step_dispatch.id,
                }
            )
        )

        [
            cls.step_create_ticket_email,
            cls.step_create_ticket_phone,
            cls.step_create_ticket,
        ] = (
            cls.env["chatbot.script.step"]
            .sudo()
            .create(
                [
                    {
                        "step_type": "question_email",
                        "message": "Could you provide us your email please.",
                        "sequence": 20,
                        "triggering_answer_ids": [
                            (4, cls.step_dispatch_create_ticket.id)
                        ],
                        "chatbot_script_id": cls.chatbot_script.id,
                    },
                    {
                        "step_type": "question_phone",
                        "message": "Could you also provide your phone please.",
                        "sequence": 21,
                        "triggering_answer_ids": [
                            (4, cls.step_dispatch_create_ticket.id)
                        ],
                        "chatbot_script_id": cls.chatbot_script.id,
                    },
                    {
                        "step_type": "create_ticket",
                        "message": "Thank you! A ticket has been created.",
                        "sequence": 22,
                        "triggering_answer_ids": [
                            (4, cls.step_dispatch_create_ticket.id)
                        ],
                        "helpdesk_team_id": cls.helpdesk_team.id,
                        "chatbot_script_id": cls.chatbot_script.id,
                    },
                ]
            )
        )
