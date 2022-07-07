from odoo.addons.mail.controllers.discuss import DiscussController


class HelpDeskDiscussController(DiscussController):
    def _get_allowed_message_post_params(self):
        res = super()._get_allowed_message_post_params()
        res.add("subject")
        return res
