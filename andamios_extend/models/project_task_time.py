from odoo import fields, models


class ProjectTaskTime(models.Model):
    _name = "project.task.time"
    _description = "Modelo personalizado para los partes de los andamios."
    _order = "date desc"

    date = fields.Date(
        string="Date",
        default=fields.Date.today(),
        required=True
    )
    type_hour = fields.Selection(
        string='Type of Hours',
        selection=[
            ('normal', 'Normal'),
            ('extra', 'Extra')
        ]
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee"
    )
    name = fields.Char(
        string="Description"
    )
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task"
    )
    subtask_id = fields.Many2one(
        comodel_name="project.task",
        string="Subtask"
    )
    project_id = fields.Many2one(
        comodel_name="project.project",
        related="task_id.project_id"
    )
    unit_amount = fields.Float(
        string="Duration"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company.id
    )
