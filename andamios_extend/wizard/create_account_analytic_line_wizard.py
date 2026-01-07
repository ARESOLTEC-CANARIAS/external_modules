from odoo import fields, models


class ModelName(models.TransientModel):
    _name = 'create.account.analytic.line.wizard'

    date = fields.Date(
        default=fields.Date.today,
        required=True,
        string="Date"
    )
    project_id = fields.Many2one(
        string='project',
        comodel_name='project.project',
        ondelete='restrict',
        required=True
    )
    task_id = fields.Many2one(
        string="task",
        comodel_name="project.task",
        domain="[('project_id', '=', project_id)]"
    )
    employee_ids = fields.Many2many(
        string='Employees',
        comodel_name='hr.employee',
        relation='employee_create_account_analytic_line_rel',
        required=True
    )
    name = fields.Char(
        string="Description"
    )
    unit_amount = fields.Float()
    extra_hours = fields.Float()
    holiday_hours = fields.Float()
    plus = fields.Float()
    diet_1 = fields.Float()
    diet_2 = fields.Float()
    diet_3 = fields.Float()

    def action_confirm(self):
        AccountAnalylicLine = self.env['account.analytic.line'].sudo()
        for employee in self.employee_ids:
            AccountAnalylicLine.create({
                'date': self.date,
                'project_id': self.project_id.id,
                'task_id': self.task_id.id if self.task_id else False,
                'plus': self.plus,
                'unit_amount': self.unit_amount,
                'extra_hours': self.extra_hours,
                'holiday_hours': self.holiday_hours,
                'diet_1': self.diet_1,
                'diet_2': self.diet_2,
                'diet_3': self.diet_3,
                'employee_id': employee.id,
                'name' : self.name
            })
