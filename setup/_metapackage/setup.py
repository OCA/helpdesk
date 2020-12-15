import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-helpdesk_mgmt',
        'odoo13-addon-helpdesk_mgmt_project',
        'odoo13-addon-helpdesk_mgmt_rating',
        'odoo13-addon-helpdesk_mgmt_timesheet',
        'odoo13-addon-helpdesk_mgmt_timesheet_time_control',
        'odoo13-addon-helpdesk_motive',
        'odoo13-addon-helpdesk_type',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
