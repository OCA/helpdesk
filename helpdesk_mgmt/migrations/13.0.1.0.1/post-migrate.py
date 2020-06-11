import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def reprocess_html_field(record, field):
    assert record._fields[field].type == "html"
    old_value = record[field]
    if old_value:
        new_value = record._fields[field].convert_to_column(old_value, record)
        if old_value != new_value:
            record.write({field: new_value})
            _logger.info(
                "Reprocessed field %r of %r (%r)", field, record, record.display_name
            )


def migrate(cr, version):
    """Reprocess existing ticket and stage descriptions."""
    env = api.Environment(cr, SUPERUSER_ID, {"active_test": False})
    for ticket in env["helpdesk.ticket"].search([]):
        reprocess_html_field(ticket, "description")
    for stage in env["helpdesk.ticket.stage"].search([]):
        reprocess_html_field(stage, "description")
