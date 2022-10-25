# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.pydantic_models.base import IdAndNameInfo
from odoo.addons.base_rest_pydantic.pydantic_models.list_metadata import ListMetadata
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.settings import HelpdeskAllSettingsInfo

_logger = logging.getLogger(__name__)


class HelpdeskSettingsService(Component):
    """Service to manage helpdesk tickets."""

    _name = "helpdesk.settings.service"
    _inherit = "base.helpdesk.rest.service"
    _usage = "helpdesk_settings"
    _description = __doc__

    @restapi.method(
        [(["/", "/all"], "GET")],
        output_param=PydanticModel(HelpdeskAllSettingsInfo),
        auth="public_or_default",
    )
    def get_all(self):
        return HelpdeskAllSettingsInfo.parse_obj(self._get_all())

    def _get_all(self):
        return {
            "categories": [categ.dict() for categ in self._get_categories()],
            "teams": [team.dict() for team in self._get_teams()],
        }

    @restapi.method(
        [(["/categories"], "GET")],
        output_param=PydanticModelList(IdAndNameInfo),
        auth="public_or_default",
    )
    def categories(self):
        data = self._get_categories()
        metadata = ListMetadata(size=len(data))
        return {"data": data, "metadata": metadata}

    def _get_categories(self):
        categories = self.env["helpdesk.ticket.category"].search([])
        result = [IdAndNameInfo.from_orm(categ) for categ in categories]
        return result

    @restapi.method(
        [(["/teams"], "GET")],
        output_param=PydanticModelList(IdAndNameInfo),
        auth="public_or_default",
    )
    def teams(self):
        data = self._get_teams()
        metadata = ListMetadata(size=len(data))
        return {"data": data, "metadata": metadata}

    def _get_teams(self):
        teams = self.env["helpdesk.ticket.team"].search([])
        result = [IdAndNameInfo.from_orm(team) for team in teams]
        return result
