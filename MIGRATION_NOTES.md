# Odoo 19.0 Migration - helpdesk_mgmt

## About This Migration
This repository contains the complete migration of the `helpdesk_mgmt` module from Odoo 18.0 to 19.0, addressing all breaking changes and ensuring full compatibility with Odoo 19.

**Migrated by:** De Bruijn Webworks  
**Date:** December 2025  
**Status:** Production-tested ✅

## What Changed in Odoo 19

### Breaking Changes Fixed

#### 1. Security Groups (`res.groups`)
- ❌ **Removed:** `category_id` field (deprecated)
- ❌ **Removed:** `users` field (deprecated)
- ✅ **Solution:** Post-init hook with direct SQL insertion

#### 2. Module Categories
- ❌ **Removed:** `ir.module.category` model entirely deprecated
- ✅ **Solution:** Commented out all module category records

#### 3. View Attributes
- ❌ **Removed:** `target="inline"` not supported
- ✅ **Solution:** Removed attribute from configuration views

#### 4. Domain Expressions
- ❌ **Removed:** `user.id` cannot be used in view domains
- ✅ **Solution:** Changed to context-based filtering with `uid`
  ```python
  # Before (18.0)
  domain="[('user_id', '=', user.id)]"
  
  # After (19.0)
  context={'search_default_user_id': uid}
  ```

#### 5. Kanban Templates
- ❌ **Removed:** `kanban_color()` helper function
- ✅ **Solution:** Direct CSS class reference
  ```xml
  <!-- Before (18.0) -->
  <div t-attf-class="#{kanban_color(record.color.raw_value)}">
  
  <!-- After (19.0) -->
  <div t-attf-class="oe_kanban_color_#{record.color.raw_value}">
  ```

#### 6. JavaScript Views
- ❌ **Simplified:** Custom `js_class` views require new asset bundling approach
- ✅ **Solution:** Simplified Dashboard to standard kanban view
- 📝 **Note:** Full JS functionality can be restored with additional asset configuration

### New Features

#### Post-Init Hook
Automatically assigns the admin user to the Helpdesk Manager group using direct SQL:

```python
def post_init_hook(env):
    """Add admin user to helpdesk manager group after installation."""
    admin_user = env.ref('base.user_admin', raise_if_not_found=False)
    manager_group = env.ref('helpdesk_mgmt.group_helpdesk_manager', raise_if_not_found=False)
    
    if admin_user and manager_group:
        env.cr.execute("""
            INSERT INTO res_groups_users_rel (gid, uid)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (manager_group.id, admin_user.id))
```

## Testing Results

All features have been tested in a production environment:

- ✅ Fresh installation successful
- ✅ Module upgrade from 18.0 successful  
- ✅ All views render correctly
  - Tickets (list, form, kanban)
  - Dashboard
  - Teams
  - Stages, Categories, Tags, Channels
- ✅ Search and filters functional
- ✅ Admin user auto-assigned to manager group
- ✅ Menu structure intact
- ✅ Portal access working
- ✅ Email integration functional
- ✅ Ticket workflows operational

## Installation

### For Fresh Installations
```bash
# Install the module
odoo-bin -d your_database -i helpdesk_mgmt

# Admin user will automatically get manager permissions
```

### For Upgrades from 18.0
```bash
# Recommended: Uninstall 18.0 version first
# Then install 19.0 version fresh
odoo-bin -d your_database -u helpdesk_mgmt
```

## Files Modified

### Core Files
- `__manifest__.py` - Version bump, post_init_hook, explicit asset paths
- `__init__.py` - Added post_init_hook function

### Security
- `security/helpdesk_security.xml` - Removed deprecated group fields

### Data
- `data/helpdesk_data.xml` - Commented out module category

### Views
- `views/res_config_settings_views.xml` - Removed target="inline"
- `views/helpdesk_ticket_views.xml` - Fixed search view domains
- `views/helpdesk_ticket_menu.xml` - Context-based filtering
- `views/helpdesk_dashboard_views.xml` - Fixed kanban_color, removed js_class

### Documentation
- `README.rst` - Updated version references

## Known Limitations

### Dashboard JavaScript Component
The advanced Dashboard component with custom JavaScript has been simplified to use a standard kanban view. The full JavaScript functionality (with `js_class="helpdesk_kanban"`) can be restored but requires:

1. Proper asset bundling configuration for Odoo 19
2. Explicit asset path definitions (no wildcards)
3. Correct loading order for JS dependencies

Current workaround provides full functionality without custom JS enhancements.

## Contributing to OCA

This migration is ready to be contributed back to the Odoo Community Association (OCA) helpdesk repository:

- **Target Repository:** https://github.com/OCA/helpdesk
- **Target Branch:** 19.0
- **Status:** Ready for Pull Request

## Support & Contact

**De Bruijn Webworks**  
Professional Odoo Development & Migration Services

For questions about this migration or Odoo consulting:
- Website: https://dev.sybrendebruijn.nl
- GitHub: https://github.com/sybdeb

## License

This module maintains the original AGPL-3.0 license from the OCA helpdesk project.

---

*Successfully migrated and tested in production - December 2025*
