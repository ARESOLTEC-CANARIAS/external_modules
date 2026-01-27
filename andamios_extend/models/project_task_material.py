from odoo import fields, models, api


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    price = fields.Monetary(string='Price', compute="_compute_price", store=True, readonly=False)
    price_subtotal = fields.Monetary(string='Subtotal', compute="_compute_subtotal_price", store=True)
    subtask_id = fields.Many2one(comodel_name="project.task")
    currency_id = fields.Many2one(related="task_id.currency_id")

    @api.depends('product_id', 'price', 'quantity')
    def _compute_subtotal_price(self):
        for record in self:
            record.write({
                'price_subtotal' : record.price * record.quantity
            })

    @api.depends('product_id', 'task_id.scaffold_id.pricelist_id')
    def _compute_price(self):
        for record in self:
            if record.product_id and record.task_id.scaffold_id and record.task_id.scaffold_id.pricelist_id:
                record.write({
                    'price' : (
                        record.task_id.scaffold_id.pricelist_id._get_product_price(
                            record.product_id,
                            quantity=record.quantity,
                            partner=record.task_id.partner_id
                        )
                    )
                })
            else:
                record.write({'price': 0})
