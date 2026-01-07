
from odoo import models, fields


class Andamios(models.Model):
    _name = 'scaffold.stage'
    _order = "sequence, name, id"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.'
    )
