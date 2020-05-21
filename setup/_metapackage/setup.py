import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-helpdesk_mgmt',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
