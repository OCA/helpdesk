# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class AttachmentService(Component):
    _name = "attachment.service"
    _inherit = "attachment.service"
    _collection = "helpdesk.rest.services"
