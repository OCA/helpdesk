# Copyright 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import partial

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestDS(SavepointCase):
    def _get_user(self, login="user_employee", groups="base.group_user", ctx=None):
        # Settings to allow to execute test as specific user, not admin
        context = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        if ctx:
            context.update(ctx)
        test_user = partial(new_test_user, context=context)
        return test_user(self.env, login=login, groups=groups)
