import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-helpdesk_mgmt',
        'odoo12-addon-helpdesk_mgmt_fieldservice',
        'odoo12-addon-helpdesk_mgmt_project',
        'odoo12-addon-helpdesk_mgmt_timesheet',
        'odoo12-addon-helpdesk_motive',
        'odoo12-addon-helpdesk_type',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
