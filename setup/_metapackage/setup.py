import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-helpdesk_mgmt>=15.0dev,<15.1dev',
        'odoo-addon-helpdesk_mgmt_project>=15.0dev,<15.1dev',
        'odoo-addon-helpdesk_mgmt_rating>=15.0dev,<15.1dev',
        'odoo-addon-helpdesk_mgmt_timesheet>=15.0dev,<15.1dev',
        'odoo-addon-helpdesk_mgmtsystem_nonconformity>=15.0dev,<15.1dev',
        'odoo-addon-helpdesk_type>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
