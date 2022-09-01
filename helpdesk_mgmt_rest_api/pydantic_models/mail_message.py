# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from odoo.addons.base_rest_pydantic.pydantic_models.base import IdAndNameInfo, IdRequest
from odoo.addons.pydantic import utils


class MailMessageBase(BaseModel):
    body: str


class MailMessageRequest(MailMessageBase):
    attachments: List[IdRequest] = Field([])


class MailMessageInfo(MailMessageBase):
    id: int
    date: datetime
    author: IdAndNameInfo = Field(None, alias="author_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class MailThreadInfo(BaseModel):
    messages: List[MailMessageInfo] = Field([], alias="message_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
