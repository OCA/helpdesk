# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    assign_method = fields.Selection(
        [
            ("manual", "Manually"),
            ("randomly", "Randomly"),
            ("balanced", "Balanced"),
            ("sequential", "Sequential"),
        ],
        string="Assignation Method",
        default="manual",
        required=True,
        help=(
            "Automatic assignation method for new tickets:\n"
            "Manually: manual\n"
            "Randomly: randomly but everyone gets the same amount\n"
            "Balanced: to the person with the least amount of open tickets\n"
            "Sequential: ensuring an even distribution among team members"
        ),
    )

    @api.onchange("user_ids")
    def _onchange_user_ids(self):
        """Set assign_method to manual if no users are assigned."""
        if not self.user_ids:
            self.assign_method = "manual"

    @api.constrains("assign_method", "user_ids")
    def _check_user_assignation(self):
        """Prevent non-manual assignation without team members."""
        for team in self:
            if not team.user_ids and team.assign_method != "manual":
                raise ValidationError(
                    _(
                        "You must have team members assigned "
                        "to change the assignation method."
                    )
                )

    def get_new_user(self):
        """Return the next user for ticket assignment based on assign_method."""
        self.ensure_one()
        user_ids = sorted(self.user_ids.ids)
        if not user_ids or self.assign_method == "manual":
            return self.env["res.users"]

        if self.assign_method == "randomly":
            return self._assign_randomly(user_ids)
        if self.assign_method == "balanced":
            return self._assign_balanced(user_ids)
        if self.assign_method == "sequential":
            return self._assign_sequential(user_ids)
        return self.env["res.users"]

    def _assign_randomly(self, user_ids):
        """Assign ticket to next user in list after previous assignment."""
        previous_ticket = self.env["helpdesk.ticket"].search(
            [("team_id", "=", self.id)],
            order="create_date desc, id desc",
            limit=1,
        )
        previous_user_id = (
            previous_ticket.user_id.id if previous_ticket.user_id else None
        )
        if previous_user_id in user_ids:
            next_index = (user_ids.index(previous_user_id) + 1) % len(user_ids)
        else:
            next_index = 0
        return self.env["res.users"].browse(user_ids[next_index])

    def _assign_balanced(self, user_ids):
        """Assign ticket to user with least open tickets."""
        read_group_res = self.env["helpdesk.ticket"].read_group(
            [("stage_id.closed", "=", False), ("user_id", "in", user_ids)],
            ["user_id"],
            ["user_id"],
        )
        count_dict = {uid: 0 for uid in user_ids}
        count_dict.update(
            {
                data["user_id"][0]: data["user_id_count"]
                for data in read_group_res
                if data["user_id"]
            }
        )
        min_user_id = min(count_dict, key=count_dict.get)
        return self.env["res.users"].browse(min_user_id)

    def _assign_sequential(self, user_ids):
        """Assign ticket to next user in sequence, cycling through team."""
        _logger.info("Assigning ticket sequentially. User IDs: %s", user_ids)
        last_ticket = self.env["helpdesk.ticket"].search(
            [("team_id", "=", self.id)],
            order="create_date desc, id desc",
            limit=1,
        )
        previous_user_id = last_ticket.user_id.id if last_ticket.user_id else None
        if previous_user_id in user_ids:
            previous_index = user_ids.index(previous_user_id)
        else:
            previous_index = -1
        next_index = (previous_index + 1) % len(user_ids)
        next_user = self.env["res.users"].browse(user_ids[next_index])
        _logger.info("Next assigned user ID: %s", next_user.id)
        return next_user
