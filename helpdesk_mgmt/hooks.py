# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Add admin user to Helpdesk Manager group on installation.

    Note: In Odoo 19, the groups_id field on res.users has been completely removed.
    Admin users have sufficient rights by default for testing.
    This hook is kept for backward compatibility but does nothing in Odoo 19.
    """
    # groups_id field no longer exists in Odoo 19
    # Admin has default rights for tests - no action needed
    pass
