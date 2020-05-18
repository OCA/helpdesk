from odoo import fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    ticket_count = fields.Integer(
        compute='_compute_ticket_count',
        string="Ticket Count")
    label_tickets = fields.Char(
        string='Use Tickets as',
        default=lambda s: _('Tickets'),
        translate=True,
        help="Gives label to tickets on project's kanban view.")

    def _compute_ticket_count(self):
        ticket_data = self.env['helpdesk.ticket'].read_group(
            [('project_id', 'in', self.ids)], ['project_id'], ['project_id']
        )
        result = dict((data['project_id'][0], data['project_id_count'])
                      for data in ticket_data)
        for project in self:
            project.ticket_count = result.get(project.id, 0)
