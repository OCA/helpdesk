import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-helpdesk_mgmt>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_project>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_mgmt_timesheet>=16.0dev,<16.1dev',
        'odoo-addon-helpdesk_type>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
