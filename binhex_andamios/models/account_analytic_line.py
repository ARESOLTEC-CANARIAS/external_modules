from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AndamiosAccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def _get_default_parent(self):
        if self._context.get('task_id'):
            return self._context.get('task_id')
        return False

    sub_task = fields.Many2one('project.task', string="Sub-Task", domain="[('parent_id', '=', task_id)]")
    owner_task_id = fields.Many2one(
        'project.task', 'Task', default=_get_default_parent)

    def write(self, vals):
        for record in self:
            if 'sub_task' in vals:
                sub_task_id = record.sub_task
                sub_task_id = self.env['project.task'].browse(int(vals['sub_task']))
            elif 'sub_task' not in vals and 'unit_amount' in vals:
                diff = abs(record.unit_amount - int(vals['unit_amount']))
                if record.unit_amount > int(vals['unit_amount']):
                    diff *= -1
        res = super(AndamiosAccountAnalyticLine, self).write(vals)
        return res
