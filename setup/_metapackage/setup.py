import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-helpdesk_mgmt',
        'odoo14-addon-helpdesk_mgmt_fieldservice',
        'odoo14-addon-helpdesk_mgmt_project',
        'odoo14-addon-helpdesk_mgmt_rating',
        'odoo14-addon-helpdesk_mgmt_sla',
        'odoo14-addon-helpdesk_mgmt_timesheet',
        'odoo14-addon-helpdesk_motive',
        'odoo14-addon-helpdesk_type',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
