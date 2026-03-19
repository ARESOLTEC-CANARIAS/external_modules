from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    order_ref = fields.Char(string='Nº order')
    contact_name = fields.Many2one(comodel_name="res.partner", string='Contact name')
    scaffold_id = fields.Many2one(comodel_name="scaffold.scaffold", string='Scaffold')

    def _error_no_account(self, task, product):
        raise UserError(_("The product %s of the task %s of the project %s doesn't have an income account") % (product.name, task.name, task.project_id.name))

    def _create_operator_hours(self, task, record):
        if task.task_type not in ['renting']:
            prod_normal_hour = self.env.ref('andamios_extend.binhex_normal_hour_operator', False)
            prod_extra_hour = self.env.ref('andamios_extend.binhex_extra_hour_operator', False)

            if prod_normal_hour:
                normal_timesheet_ids = self.env['project.task.time'].search([
                    ('subtask_id', '=', task.id),
                    ('task_id', '=', task.parent_id.id),
                    ('type_hour', '=', 'normal')
                ])
                if normal_timesheet_ids:
                    normal_hour_total = sum(normal_timesheet_ids.mapped('unit_amount'))

                    if normal_hour_total > 0:
                        prod_normal_line = record.invoice_line_ids.filtered(
                            lambda line : line.product_id.id == prod_normal_hour.id and line.task_id.id == task.id
                        )
                        if prod_normal_line:
                            prod_normal_line[-1].with_context(check_move_validity=False).sudo().write({
                                'quantity': (prod_normal_line.quantity + normal_hour_total)
                            })
                            self.env.cr.commit()
                        else:
                            if not prod_normal_hour.property_account_income_id:
                                self._error_no_account(task, prod_normal_hour)

                            record.invoice_line_ids = [(0, 0, {
                                'currency_id' : self.env.user.company_id.currency_id.id,
                                'move_id': record.id,
                                'product_id': prod_normal_hour.id,
                                'name': prod_normal_hour.name,
                                'quantity': normal_hour_total,
                                'product_uom_id': prod_normal_hour.uom_id.id,
                                'price_unit': task.scaffold_id.normal_hour_price,
                                'account_id': prod_normal_hour.property_account_income_id.id,
                                'tax_ids': prod_normal_hour.taxes_id.ids,
                                # 'analytic_account_id': task.project_id.analytic_account_id.id,
                                'analytic_distribution': {
                                    task.project_id.account_id.id: 100,
                                },
                                'task_id': task.id,
                            })]

            if prod_extra_hour:
                extra_timesheet_ids = self.env['project.task.time'].search([
                    ('subtask_id', '=', task.id),
                    ('task_id', '=', task.parent_id.id),
                    ('type_hour', '=', 'extra')
                ])

                if extra_timesheet_ids:
                    extra_hour_total = sum(extra_timesheet_ids.mapped('unit_amount'))
                    if extra_hour_total > 0:
                        prod_extra_line = record.invoice_line_ids.filtered(
                            lambda line : line.product_id.id == prod_extra_hour.id and line.task_id.id == task.id
                        )

                        if prod_extra_line:
                            prod_extra_line[-1].with_context(check_move_validity=False).sudo().write({
                                'quantity': (prod_extra_line.quantity + extra_hour_total)
                            })
                            self.env.cr.commit()
                        else:
                            if not prod_extra_hour.property_account_income_id:
                                self._error_no_account(task, prod_extra_hour)

                            record.invoice_line_ids = [(0, 0, {
                                'currency_id' : self.env.user.company_id.currency_id.id,
                                'move_id': record.id,
                                'product_id': prod_extra_hour.id,
                                'name': prod_extra_hour.name,
                                'quantity': extra_hour_total,
                                'product_uom_id': prod_extra_hour.uom_id.id,
                                'price_unit': task.scaffold_id.extra_hour_price,
                                'account_id': prod_extra_hour.property_account_income_id.id,
                                'tax_ids': prod_extra_hour.taxes_id.ids,
                                # 'analytic_account_id': task.project_id.analytic_account_id.id,
                                'analytic_distribution': {
                                    task.project_id.account_id.id: 100,
                                },
                                'task_id': task.id,
                            })]

    def _create_materials_lines(self, task, record):
        for material_id in task.parent_id.material_ids:
            if material_id.subtask_id.id == task.id:
                if not material_id.product_id.property_account_income_id:
                    self._error_no_account(task, material_id.product_id)

                record.invoice_line_ids = [(0, 0, {
                    'currency_id' : self.env.user.company_id.currency_id.id,
                    'move_id': record.id,
                    'product_id': material_id.product_id.id,
                    'name': material_id.product_id.name,
                    'quantity': material_id.quantity,
                    'product_uom_id': material_id.product_id.uom_id.id,
                    'price_unit': material_id.price,
                    'account_id': material_id.product_id.property_account_income_id.id,
                    'tax_ids': material_id.product_id.taxes_id.ids,
                    # 'analytic_account_id': task.project_id.analytic_account_id.id,
                    'analytic_distribution': {
                        task.project_id.account_id.id: 100,
                    },
                    'task_id': task.id,
                })]

    def _create_move_line(self, task, record):
        if not task.timesheet_product_id:
            raise UserError(_("The task ") + task.name + _(" of the project ") + task.project_id.name + _(" doesn't have a related service"))
        elif not task.timesheet_product_id.property_account_income_id and not task.timesheet_product_id.categ_id.property_account_income_categ_id:
            raise UserError(_("The service ") + task.timesheet_product_id.name + _(" of the task ") + task.name + _(" of the project ") + task.project_id.name + _(" doesn't have an income account"))
        elif not task.timesheet_product_id.taxes_id:
            raise UserError(_("The service ") + task.timesheet_product_id.name + _(" of the task ") + task.name + _(" of the project ") + task.project_id.name + _(" doesn't have any taxes"))
        elif not task.task_type:
            raise UserError(_("The task ") + task.name + _(" of the project ") + task.project_id.name + _(" doesn't have a type selected"))
        else:
            product_id = task.timesheet_product_id
            qty = 1
            end_date = False
            start_date = False
            number_of_days = 1
            rental_qty = 1
            rental = False
            price_ = task.scaffold_id.pricelist_id._get_product_price_rule(product_id, quantity=(qty or 1))[0]
            if task.task_type == 'assembly':
                qty = task.cubic_meters
                start_date = task.assembly_date
                end_date = task.assembly_date
                price_ = task.scaffold_id.assembly_price
            elif task.task_type == 'disassembly':
                qty = task.cubic_meters
                start_date = task.disassembly_date
                end_date = task.disassembly_date
                price_ = task.scaffold_id.disassembly_price
            elif task.task_type == 'renting':
                number_of_days = (task.renting_end_date - task.renting_start_date).days + 1
                qty = number_of_days * task.cubic_meters
                rental_qty = task.cubic_meters
                start_date = task.renting_start_date
                end_date = task.renting_end_date
                price_ = task.scaffold_id.renting_price
                rental = True
            elif task.task_type == 'extra':
                qty = 0

            if qty > 0:
                account_id = product_id.property_account_income_id \
                    or product_id.categ_id.property_account_income_categ_id
                if not account_id:
                    self._error_no_account(task, product_id)

                self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'move_id': record.id,
                    'product_id': product_id.id,
                    'name': product_id.name,
                    'quantity': qty,
                    'rental_qty': rental_qty,
                    'rental': rental,
                    'number_of_days': number_of_days,
                    'product_uom_id': product_id.uom_id.id,
                    'price_unit': price_,
                    'account_id': account_id.id,
                    'tax_ids': product_id.taxes_id.ids,
                    'start_date': start_date,
                    'end_date': end_date,
                    # 'analytic_account_id': task.project_id.analytic_account_id.id,
                    'analytic_distribution': {
                        task.project_id.account_id.id: 100,
                    },
                    'task_id': task.id,
                })

    @api.model
    def _create_move_lines(self, record=False):
        if not record:
            record = self
        if isinstance(record, models.BaseModel):
            tasks = record.cubic_meters_tasks.sorted(key=lambda r: r.parent_id.id)
        else:
            tasks = record.get('cubic_meters_tasks', False)
            if tasks and isinstance(tasks[0], int):
                tasks = self.env['project.task'].browse(tasks).sorted(key=lambda r: r.parent_id.id)
            else:
                tasks = []
        for task in tasks:
            if not record.invoice_line_ids.filtered(
                lambda i : i.display_type == 'line_section' and i.name == task.name
            ):
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'name': task.name,
                    'move_id': record.id,
                    'display_type': 'line_section',
                    'task_id': task.id,
                    'show_line_amount': False,
                })
            if record.move_type == "out_refund":
                task.invoiced = False

            if task.task_type == 'partial':
                for task_partial in task.partial_task_ids:
                    self._create_move_line(task_partial, record)
                    self._create_materials_lines(task_partial, record)
                    self._create_operator_hours(task_partial, record)
            else:
                self._create_move_line(task, record)
                self._create_materials_lines(task, record)
                self._create_operator_hours(task, record)

    @api.model_create_multi
    def create(self, vals):
        records = self.env['account.move']
        for list in vals:
            record = super().create(list)
            scaffold_ids = record.cubic_meters_tasks.mapped('scaffold_id').ids
            self.env['scaffold.scaffold'].browse(scaffold_ids).write({'account_move_ids': [(4, record.id)]})
            records |= record
        return records

    def action_confirm(self):
        self.cubic_meters_tasks.write({
            'invoiced' : True
        })
        return super().action_confirm()

    def unlink(self):
        self.cubic_meters_tasks.write({
            'invoiced' : False
        })
        return super().unlink()
