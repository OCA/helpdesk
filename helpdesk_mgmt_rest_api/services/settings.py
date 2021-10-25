# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel

_logger = logging.getLogger(__name__)


class HelpdeskSettingsService(Component):
    """Service to manage helpdesk tickets."""

    _name = "helpdesk.settings.service"
    _inherit = [
        "base.helpdesk.rest.service",
    ]
    _usage = "helpdesk_settings"
    _description = __doc__

    @restapi.method(
        [(["/", "/all"], "GET")],
        output_param=restapi.Datamodel("helpdesk.all.settings.output"),
        auth="public_or_default",
    )
    def get_all(self):
        return self.env.datamodels["helpdesk.all.settings.output"].load(self._get_all())

    def _get_all(self):
        return {
            "categories": self._get_categories(),
            "teams": self._get_teams(),
        }

    @restapi.method(
        [(["/categories"], "GET")],
        output_param=restapi.Datamodel("helpdesk.category.output", is_list=True),
        auth="public_or_default",
    )
    def categories(self):
        return self.env.datamodels["helpdesk.category.output"].load(self._get_categories(), many=True)

    def _get_categories(self):
        return (
            self.env["helpdesk.ticket.category"]
            .search([])
            .jsonify(self._jsonify_id_and_name())
        )

    @restapi.method(
        [(["/teams"], "GET")],
        output_param=restapi.Datamodel("helpdesk.team.output", is_list=True),
        auth="public_or_default",
    )
    def teams(self):
        return self.env.datamodels["helpdesk.team.output"].load(self._get_teams(), many=True)

    def _get_teams(self):
        return self.env["helpdesk.ticket.team"].search([]).jsonify(self._jsonify_id_and_name())

    def _jsonify_id_and_name(self):
        return ["id", "name"]


class HelpdeskAllSettingsOutput(Datamodel):
    _name = "helpdesk.all.settings.output"

    categories = fields.NestedModel(
        "helpdesk.category.output", required=False, allow_none=True, many=True
    )
    teams = fields.NestedModel(
        "helpdesk.team.output", required=False, allow_none=True, many=True
    )
