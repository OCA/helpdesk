from . import controllers
from . import models
from . import wizards


def post_init_hook(env):
    """Add admin users to Helpdesk Manager group after module installation"""
    try:
        # Use SQL to add admin to the group (Odoo 19 compatible)
        manager_group = env.ref('helpdesk_mgmt.group_helpdesk_manager', raise_if_not_found=False)
        admin_user = env.ref('base.user_admin', raise_if_not_found=False)
        
        if manager_group and admin_user:
            # Direct SQL insert into the m2m table
            env.cr.execute("""
                INSERT INTO res_groups_users_rel (gid, uid)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (manager_group.id, admin_user.id))
    except Exception as e:
        # Log but don't fail installation
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning(f"Could not add admin to Helpdesk Manager group: {e}")
