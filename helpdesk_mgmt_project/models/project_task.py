from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    ticket_count = fields.Integer(
        compute='_compute_ticket_count',
        string="Ticket Count")

    def _compute_ticket_count(self):
        ticket_data = self.env['helpdesk.ticket'].read_group(
            [('task_id', 'in', self.ids)], ['task_id'], ['task_id']
        )
        result = dict((data['task_id'][0], data['task_id_count'])
                      for data in ticket_data)
        for task in self:
            task.ticket_count = result.get(task.id, 0)
