from odoo import models, fields, api
from random import randint

import logging
_logger = logging.getLogger(__name__)


class Scaffold(models.Model):
    _inherit = 'scaffold.scaffold'

    alias = fields.Char(string='Alias')
    normal_hour_price = fields.Monetary(
        string='Normal hour price',
        compute='_compute_prices',
        store=True,
        readonly=False)
    extra_hour_price = fields.Monetary(
        string='Extra hour price',
        compute='_compute_prices',
        store=True,
        readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    tag_ids = fields.Many2many('scaffold.tag', string='Tags')

    assembly_price = fields.Monetary(string="Assembly price", store=True, readonly=False, compute="_compute_prices")
    disassembly_price = fields.Monetary(string="Disassembly price", store=True, readonly=False, compute="_compute_prices")

    renting_price = fields.Monetary(string="Renting Price", store=True, readonly=False, compute="_compute_prices")

    not_invoiced_tasks = fields.Many2many(
        comodel_name="project.task",
        string="Not invoiced tasks",
        compute="_compute_not_invoiced_tasks",
    )

    def _compute_not_invoiced_tasks(self):
        for record in self:
            if not record.project_id:
                record.not_invoiced_tasks = self.env['project.task']
            else:
                record.not_invoiced_tasks = self.env['project.task'].search([
                    ('project_id', '=', record.project_id.id),
                    ('scaffold_id', '=', record.id),
                    ('invoiced', '=', False),
                    ('active', '=', True),
                    ('is_parent', '=', False),
                ])

    @api.model
    def _get_product_pricelist(self, pricelist, product, qty, partner):
        return pricelist._get_product_price(product, quantity=qty, partner=partner)

    @api.depends('order_ids.order_line', 'pricelist_id', 'cubic_meters')
    def _compute_prices(self):
        for record in self:
            normal_hour_operator_product = self.env.ref('andamios_extend.binhex_normal_hour_operator', raise_if_not_found=False)
            extra_hour_operator_product = self.env.ref('andamios_extend.binhex_extra_hour_operator', raise_if_not_found=False)

            if not normal_hour_operator_product or not extra_hour_operator_product:
                record.normal_hour_price = 0
                record.extra_hour_price = 0
                record.assembly_price = 0
                record.disassembly_price = 0
                record.renting_price = 0
                continue
            lines = record.mapped('order_ids').mapped('order_line')

            assembly_line = lines.filtered(
                lambda line: line.product_id.id == record.assembly_prod_id.id
            )
            disassembly_line = lines.filtered(
                lambda line: line.product_id.id == record.disassembly_prod_id.id
            )
            normal_hour_line = lines.filtered(
                lambda line: line.product_id.id == normal_hour_operator_product.id
            )
            extra_hour_line = lines.filtered(
                lambda line: line.product_id.id == extra_hour_operator_product.id
            )
            renting_line = lines.filtered(
                lambda line: line.product_id.id == record.renting_prod_id.id
            )

            if assembly_line:
                record.assembly_price = assembly_line[-1].price_unit
            elif record.pricelist_id:
                record.assembly_price = record._get_product_pricelist(
                    record.pricelist_id,
                    record.assembly_prod_id,
                    record.cubic_meters,
                    record.client_id
                )
            else:
                record.assembly_price = record.assembly_prod_id.list_price

            if disassembly_line:
                record.disassembly_price = disassembly_line[-1].price_unit
            elif record.pricelist_id:
                record.disassembly_price = record._get_product_pricelist(
                    record.pricelist_id,
                    record.disassembly_prod_id,
                    record.cubic_meters,
                    record.client_id
                )
            else:
                record.disassembly_price = record.disassembly_prod_id.list_price

            if normal_hour_line:
                record.normal_hour_price = normal_hour_line[-1].price_unit
            elif record.pricelist_id:
                record.normal_hour_price = record._get_product_pricelist(
                    record.pricelist_id,
                    normal_hour_operator_product,
                    record.cubic_meters,
                    record.client_id
                )
            else:
                record.normal_hour_price = normal_hour_operator_product.list_price

            if extra_hour_line:
                record.extra_hour_price = extra_hour_line[-1].price_unit
            elif record.pricelist_id:
                record.extra_hour_price = record._get_product_pricelist(
                    record.pricelist_id,
                    extra_hour_operator_product,
                    record.cubic_meters,
                    record.client_id
                )
            else:
                record.extra_hour_price = extra_hour_operator_product.list_price

            if renting_line:
                record.renting_price = renting_line[-1].price_unit
            elif record.pricelist_id:
                record.renting_price = record._get_product_pricelist(
                    record.pricelist_id,
                    record.renting_prod_id,
                    record.cubic_meters,
                    record.client_id
                )
            else:
                record.renting_price = record.renting_prod_id.list_price

    def create_task(self):
        res = super().create_task()
        if self.fast_task:
            task = self.env['project.task'].create({
                'name': self.name,
                'scaffold_id': self.id,
                'project_id': self.project_id.id,
                'activity_user_id': self.supervisor_id.id,
                'partner_id' : self.client_id.id,
                'description': self.description,
                'assembly_sub_task': self.fast_task,
                'disassembly_sub_task': self.fast_task,
                'create_all_renting' : self.fast_task,
            })
            task.create_renting_subtask()
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id' : task.id,
                'context': {
                    'active_id' : task.id,
                }
            }
        return res

    def create_invoice(self):
        self.ensure_one()
        res = super().create_invoice()
        res['context'].update({
            'default_scaffold_id': self.id,
        })
        return res


class ScaffoldTag(models.Model):
    _name = 'scaffold.tag'
    description = "Scaffold tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Name", required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
