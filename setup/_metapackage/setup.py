import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-helpdesk_mgmt>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_account>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_activity>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_assign_method>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_fieldservice>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_merge>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_portal_follower>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_project>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_project_domain>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_project_stage>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_rating>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_sale>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_sla>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_stage_validation>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_stock>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_template>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_timesheet>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_motive>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_portal_priority>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_portal_restriction>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_product>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_ticket_close_inactive>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_ticket_open_tab>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_ticket_partner_response>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_ticket_related>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_timesheet_time_type>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_type>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
