import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-helpdesk",
    description="Meta package for oca-helpdesk Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-helpdesk_mgmt',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
