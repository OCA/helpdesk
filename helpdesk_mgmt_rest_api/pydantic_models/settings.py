# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import List

from pydantic import BaseModel

from odoo.addons.base_rest_pydantic.pydantic_models.base import IdAndNameInfo


class HelpdeskAllSettingsInfo(BaseModel):
    categories: List[IdAndNameInfo]
    teams: List[IdAndNameInfo]
