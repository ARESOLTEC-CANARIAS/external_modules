from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AndamiosAccountMove(models.Model):
    _inherit = 'account.move'

    cubic_meters_tasks = fields.Many2many('project.task', string="Cubic Meters Tasks(m3)")
    boolean_task = fields.Boolean(string="Show Tasks")
    project_id = fields.Many2one('project.project', string="Project")

    def _create_move_lines(self, record=False):
        if not record:
            record = self
        current_section = False
        for task in record.cubic_meters_tasks.sorted(key=lambda r: r.parent_id.id):
            if task.parent_id != current_section:
                current_section = task.parent_id
                move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'name': current_section.name,
                    'move_id': record.id,
                    'display_type': 'line_section',
                    'task_id': current_section.id,
                    'show_line_amount': False,
                })
            if record.move_type == "out_refund":
                task.invoiced = False
            if record.move_type != "out_invoice":
                task.scaffold_id.account_move_ids = [(4, record.id)]
                continue
            task.invoiced = True

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
                if task.task_type == 'assembly':
                    qty = task.cubic_meters
                    start_date = task.assembly_date
                    end_date = task.assembly_date
                elif task.task_type == 'disassembly':
                    qty = task.cubic_meters
                    start_date = task.disassembly_date
                    end_date = task.disassembly_date
                elif task.task_type == 'renting':
                    number_of_days = (task.renting_end_date - task.renting_start_date).days + 1
                    qty = number_of_days * task.cubic_meters
                    rental_qty = task.cubic_meters
                    start_date = task.renting_start_date
                    end_date = task.renting_end_date
                    rental = True
                elif task.task_type == 'extra':
                    qty = 0

                price_ = task.scaffold_id.pricelist_id._get_product_price_rule(product_id.id, quantity=(qty or 1))[0]
                if qty > 0:
                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
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
                        'account_id': product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': product_id.taxes_id.ids,
                        'start_date': start_date,
                        'end_date': end_date,
                        # 'analytic_account_id': task.project_id.analytic_account_id.id,
                        'analytic_distribution': {
                            task.project_id.account_id.id: 100,
                        },
                        'task_id': task.id
                    })
                    record.invoice_line_ids = [(4, move_line.id)]

                # Add to the invoice the timesheet related with the task in task parent
                ts_prod = self.env.ref('sale_timesheet.time_product', False)
                if ts_prod:
                    timesheet_ids = self.env['account.analytic.line'].search([('sub_task', '=', task.id)])
                    if len(timesheet_ids) > 0:
                        for tsheet in timesheet_ids:
                            ts_move_line = self.env['account.move.line'].search([
                                ('id', 'in', record.invoice_line_ids.ids),
                                ('product_id', '=', ts_prod.id)
                            ])
                            if not ts_move_line:
                                price_ = task.scaffold_id.pricelist_id._get_product_price_rule(ts_prod.id, quantity=(tsheet.unit_amount or 1))[0]
                                ts_move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                                    'currency_id' : self.env.user.company_id.currency_id.id,
                                    'move_id': record.id,
                                    'product_id': ts_prod.id,
                                    'name': ts_prod.name,
                                    'quantity': tsheet.unit_amount,
                                    'rental_qty': rental_qty,
                                    'rental': rental,
                                    'number_of_days': number_of_days,
                                    'product_uom_id': ts_prod.uom_id.id,
                                    'price_unit': price_,
                                    'account_id': ts_prod.property_account_income_id.id,
                                    'tax_ids': ts_prod.taxes_id.ids,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    # 'analytic_account_id': task.project_id.analytic_account_id.id,
                                    'analytic_distribution': {
                                        task.project_id.account_id.id: 100,
                                    },
                                    'task_id': task.id,
                                })
                                record.invoice_line_ids = [(4, ts_move_line.id)]
                            else:
                                ts_move_line.with_context(check_move_validity=False).sudo().write({'quantity': (ts_move_line.quantity + tsheet.unit_amount)})
                                self.env.cr.commit()

    @api.model_create_multi
    def create(self, vals):
        records = self.env['account.move']
        for list in vals:
            if self.env.context.get('project_ref_id'):
                list['project_id'] = int(self.env.context.get('project_ref_id'))
            record = super(AndamiosAccountMove, self).create(list)
            record._create_move_lines()
            if self.env.context.get('scaffold_ref_id'):
                self.env['scaffold.scaffold'].browse(int(self.env.context.get('scaffold_ref_id'))).write({'account_move_ids': [(4, record.id)]})
            records |= record
        return records

    def write(self, vals):
        for rec in self:
            tasks = rec.cubic_meters_tasks.ids
            super(AndamiosAccountMove, rec).write(vals)
            old_scaffold_ids = set()
            new_scaffold_ids = set()
            if vals.get('invoice_line_ids') or vals.get('cubic_meters_tasks'):
                for line in rec.invoice_line_ids:
                    old_scaffold_ids.add(line.task_id.scaffold_id.id)
            else:
                continue

            if vals.get('cubic_meters_tasks'):
                for line in rec.line_ids:
                    line.with_context(check_move_validity=False).unlink()
                rec._create_move_lines()
                for line in rec.invoice_line_ids:
                    new_scaffold_ids.add(line.task_id.scaffold_id.id)

            if vals.get('invoice_line_ids'):
                for line in rec.invoice_line_ids:
                    new_scaffold_ids.add(line.task_id.scaffold_id.id)

            deleted_scaffold_ids = list(old_scaffold_ids - new_scaffold_ids)
            for p in deleted_scaffold_ids:
                rec.env['scaffold.scaffold'].browse(p).account_move_ids = [(3, rec.id)]
            added_scaffold_ids = list(new_scaffold_ids - old_scaffold_ids)
            for p in added_scaffold_ids:
                rec.env['scaffold.scaffold'].browse(p).account_move_ids = [(4, rec.id)]

            self.env['project.task'].browse(tasks)._compute_invoiced()
        return

    # NO debería de funcionar, lo dejo comentado por si acaso
    # def assing_account_move_to_scaffold(self):
    #     if not record:
    #         record = self
    #     scaffold_ids = set()
    #     for line in self.invoice_line_ids:
    #         scaffold_ids.append(line.task_id.scaffold_id.id)
    #     self.env['scaffold.scaffold'].browse(p).order_ids = [(3,self.id)]


class AndamiosSalesOrderLine(models.Model):
    _inherit = "account.move.line"

    rental = fields.Boolean(default=False)
    task_id = fields.Many2one("project.task", ondelete="restrict", string="Task")
    number_of_days = fields.Float(readonly=True, string='Number of days')
    rental_qty = fields.Float(string='Cubic Meters')

    @api.onchange("product_id")
    def _update_qty(self):
        if self.product_id.rented_product_id:
            self.rental = True
        else:
            self.rental = False

    @api.onchange("start_date", "end_date")
    def _days_amount(self):
        if self.start_date and self.end_date and self.product_id.uom_id in self.env.company.day_udm_ids and self.rental is True:
            dif = (self.end_date - self.start_date).days + 1
            self.quantity = dif * self.rental_qty
        elif self.product_id.uom_id not in self.env.company.day_udm_ids:
            if not self.start_date and not self.end_date:
                return
            elif self.start_date and not self.end_date:
                self.end_date = self.start_date
                self.quantity = 1
            elif self.end_date and not self.start_date:
                self.start_date = self.end_date
                self.quantity = 1
            else:
                self.quantity = (self.end_date - self.start_date).days + 1
