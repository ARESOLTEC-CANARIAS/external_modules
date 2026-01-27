from odoo import fields, models, _


class ScaffoldPartialReport(models.TransientModel):
    _name = 'scaffold.partial.report.wizard'

    scaffold_id = fields.Many2one(
        string='Scaffold',
        comodel_name='scaffold.scaffold'
    )
    task_id = fields.Many2one(related='scaffold_id.task_id')
    task_ids = fields.Many2many(
        string='Tasks',
        comodel_name='project.task',
        relation='scaffold_partial_report_task_rel',
    )

    def _get_description(self):
        return _("<p>Parte parcial de %s, contiene los siguientes partes: %s .</p>" % (self.task_id.name, ', '.join(self.task_ids.mapped('name'))))

    def create_partial_task(self):
        vals = {
            'is_parent': False,
            'scaffold_id' : self.scaffold_id.id,
            'partner_id' : self.task_id.partner_id.id,
            # 'partner_email' : self.task_id.partner_id.email,
            'project_id' : self.task_id.project_id.id,
            'description' : self._get_description(),
            'parent_id' : self.task_id.id,
            'sale_line_id': False,
            'task_type': 'partial',
            'name': self.task_id.name + '-' + self.env['ir.sequence'].next_by_code('partial.parts'),
            'partial_task_ids': [(6, 0, self.task_ids.ids)],
        }

        res = self.env['project.task'].create(vals)
        self.task_ids.write({'facture_in_partial': True})
        self.env.cr.commit()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': res.id,
            'target': 'current',
        }
