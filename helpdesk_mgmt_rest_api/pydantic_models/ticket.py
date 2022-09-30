from datetime import datetime

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel, EmailStr, Field

from odoo.addons.base_rest_attachment.pydantic_models.attachment import AttachableInfo
from odoo.addons.base_rest_pydantic.pydantic_models.base import IdAndNameInfo, IdRequest
from odoo.addons.pydantic import utils

from ..pydantic_models.mail_message import MailThreadInfo


class HelpdeskPartnerRequest(BaseModel):
    email: EmailStr
    name: str
    lang: str = None


class HelpdeskTicketInfo(AttachableInfo, MailThreadInfo):
    id: int
    name: str
    description: str
    create_date: datetime
    last_stage_update: datetime
    category: IdAndNameInfo = Field(None, alias="categ_id")
    team: IdAndNameInfo = Field(None, alias="team_id")
    stage: IdAndNameInfo = Field(None, alias="stage_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class HelpdeskTicketRequest(BaseModel, metaclass=ExtendableModelMeta):
    name: str
    description: str
    partner: HelpdeskPartnerRequest = Field(None)
    category: IdRequest = Field(None)
    team: IdRequest = Field(None)
