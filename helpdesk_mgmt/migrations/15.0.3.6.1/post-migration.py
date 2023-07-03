# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Delete noupdate record as it will not be used anymore."""
    openupgrade.delete_records_safely_by_xml_id(
        env, ["helpdesk_mgmt.assignment_email_template"]
    )
