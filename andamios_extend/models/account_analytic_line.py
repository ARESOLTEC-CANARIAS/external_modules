from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    extra_hours = fields.Float()
    holiday_hours = fields.Float()
    plus = fields.Float()
    diet_1 = fields.Float()
    diet_2 = fields.Float()
    diet_3 = fields.Float()
