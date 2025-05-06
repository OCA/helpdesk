from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ticket_properties_search = fields.Char(
        store=False, search="_search_in_ticket_category_all_properties"
    )

    ticket_properties = fields.Properties(
        "Properties",
        definition="category_id.ticket_properties_definition",
        copy=True,
    )

    @api.model
    def _search_in_ticket_category_all_properties(self, operator, value):
        if operator not in ["ilike", "=", "like"]:
            raise NotImplementedError("Only text search operators are supported")

        # Convert value to string to prevent SQL injection issues
        value = str(value)

        query = """
            SELECT id FROM helpdesk_ticket
            WHERE ticket_properties::text ILIKE %s
        """
        like_pattern = f"%{value}%"
        self.env.cr.execute(query, (like_pattern,))
        ids = [row[0] for row in self.env.cr.fetchall()]
        return [("id", "in", ids)]
