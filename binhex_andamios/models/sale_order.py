from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class AndamiosSales(models.Model):
    _inherit = 'sale.order'

    andamio_ids = fields.Many2many('scaffold.scaffold', "sale_order_andamio", "id2", "id1", string="Scaffolds", copy=False)
    andamio_ids_size = fields.Integer(string="Scaffold Qty", compute="_andamio_id_size_update")

    def write(self, vals):
        for rec in self:
            if vals.get('order_line'):
                old_scaffolds = rec._get_unique_scaffolds()
            super(AndamiosSales, rec).write(vals)
            if vals.get('order_line'):
                actual_scaffolds = rec._get_unique_scaffolds()
                deleted_scaffolds = old_scaffolds - actual_scaffolds
                for scaff in deleted_scaffolds:
                    scaff.order_ids = [(3, rec.id)]
                    rec.andamio_ids = [(3, scaff.id)]
                added_scaffold_ids = list(actual_scaffolds - old_scaffolds)
                for p in added_scaffold_ids:
                    rec.env['scaffold.scaffold'].browse(p).order_ids = [(4, rec.id)]
        return

    @api.model
    def view_init(self, fields_list):
        if self._context.get('scaffold_id'):
            for sorder in self:
                for order in sorder.order_line:
                    if order.order_id.pricelist_id:
                        order.price_unit = order._get_display_price(order.product_id)
        return super(AndamiosSales, self).view_init(fields_list)

    @api.model_create_multi
    def create(self, vals):
        records = self.env['sale.order']
        for list in vals:
            record = super(AndamiosSales, self).create(list)
            if self._context.get('scaffold_id'):
                self.env['scaffold.scaffold'].browse(self._context.get('scaffold_id')).write({'order_ids': [(4, record.id)]})
            records |= record
        return records

    def _get_unique_scaffolds(self):
        unique_scaffolds = set()
        for line in self.order_line:
            if line.scaffold_id:
                unique_scaffolds.add(line.scaffold_id)
        return unique_scaffolds

    def action_create_scaffold(self):
        sections = self.env['sale.order.line'].search([('order_id', '=', self.id), ('display_type', '=', 'line_section'),])
        scaffold_id = False
        if not sections:
            create_once = True
            for line in self.order_line:
                if line.product_id.product_tmpl_id in self.env.company.scaffold_services and not line.scaffold_id and line.display_type is False:
                    if create_once:
                        name = self.name + '-' + str(len(self.andamio_ids) + 1)
                        scaffold_id = self.env['scaffold.scaffold'].create({'name': name, 'client_id': self.partner_id.id, 'order_ids': [self.id], 'pricelist_id': self.pricelist_id.id})
                        self.andamio_ids = [(4, scaffold_id.id)]
                        create_once = False
                    line.scaffold_id = scaffold_id
        else:
            create = False
            for line in self.order_line:
                if line.display_type == 'line_section':
                    create = True
                    continue
                if line.product_id.product_tmpl_id in self.env.company.scaffold_services and not line.scaffold_id and line.display_type is False:
                    if create:
                        scaffold_id = self.env['scaffold.scaffold'].create({'client_id': self.partner_id.id, 'order_ids': [self.id], 'pricelist_id': self.pricelist_id.id})
                        self.andamio_ids = [(4, scaffold_id.id)]
                        create = False
                    line.scaffold_id = scaffold_id

        if not self.project_ids:
            project_id = self.env['project.project'].create({'name': self.name, 'partner_id': self.partner_id.id, 'sale_order_id': self.id})

            self.project_ids = [(4, project_id.id)]
        parent_tasks = {}
        for scaffold in self._get_unique_scaffolds():
            if not scaffold.project_id:
                scaffold.project_id = project_id.id
            if not scaffold.task_id:
                parent_task_id = self.env['project.task'].create({
                    'name': scaffold.name,
                    'scaffold_id': scaffold.id,
                    'partner_id': self.partner_id.id,
                    # 'partner_email': self.partner_id.email,
                    'project_id': fields.first(self.project_ids).id,
                    'cubic_meters': 0,
                    'sale_line_id': False,
                })
                parent_tasks[scaffold.id] = parent_task_id.id
        child_tasks_id = []
        for task in self.tasks_ids:
            child_tasks_id.append(task)
        if child_tasks_id:
            if parent_tasks:
                for task in child_tasks_id:
                    if task.sale_line_id.product_id.product_tmpl_id in self.env.company.scaffold_services:
                        sale_line = task.sale_line_id
                        product_tmpl_id = sale_line.product_id.product_tmpl_id
                        if product_tmpl_id.scaffold_service_type in ['assembly', 'disassembly']:
                            task.write({'scaffold_id': sale_line.scaffold_id, 'parent_id': parent_tasks[sale_line.scaffold_id.id], 'is_parent': False, 'allow_subtasks': False})
                        if product_tmpl_id.scaffold_service_type == 'assembly':
                            task.write({'cubic_meters': sale_line.product_uom_qty, 'task_type': sale_line.task_type, 'timesheet_product_id': sale_line.scaffold_id.assembly_prod_id})
                            task.parent_id.write({'assembly_date': sale_line.start_date, 'assembly_sub_task': True})
                            if sale_line.start_date:
                                task.assembly_date = sale_line.start_date
                        elif product_tmpl_id.scaffold_service_type == 'disassembly':
                            task.write({'cubic_meters': sale_line.product_uom_qty, 'task_type': sale_line.task_type, 'timesheet_product_id': sale_line.scaffold_id.disassembly_prod_id})
                            task.parent_id.write({'disassembly_date': sale_line.end_date, 'disassembly_sub_task': True})
                            if sale_line.end_date:
                                task.disassembly_date = sale_line.end_date
                        elif product_tmpl_id.scaffold_service_type == 'extension':
                            task.write({'cubic_meters': sale_line.product_uom_qty, 'assembly_date': sale_line.start_date, 'disassembly_date': sale_line.end_date, 'timesheet_product_id': sale_line.scaffold_id.extension_prod_id})
                        if task.parent_id.cubic_meters == 0:
                            task.parent_id.cubic_meters = task.cubic_meters

        if scaffold_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Scaffold'),
                'view_mode': 'form',
                'res_model': 'scaffold.scaffold',
                'res_id': scaffold_id.id,
            }

    def action_show_andamios_treeview(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scaffold'),
            'view_mode': 'list,form',
            'res_model': 'scaffold.scaffold',
            # 'view_id': self.env.ref('binhex_andamios.andamios_list').id,
            'domain': [('id', 'in', self.andamio_ids.ids)],
        }

    def _andamio_id_size_update(self):
        for record in self:
            record.andamio_ids_size = len((record.andamio_ids).ids)

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     super(AndamiosSales, self).onchange_partner_id()
    #     if self._context.get('default_pricelist_id'):
    #         self.update({'pricelist_id': self._context.get('default_pricelist_id')})
    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        super()._compute_pricelist_id()
        for order in self:
            if order._context.get('default_pricelist_id'):
                order.update({'pricelist_id': order._context.get('default_pricelist_id')})


class AndamiosSalesOrderLine(models.Model):
    _inherit = "sale.order.line"

    scaffold_id = fields.Many2one('scaffold.scaffold', string='Scaffold', copy=False)
    task_type = fields.Selection(related='product_id.product_tmpl_id.scaffold_service_type')
    user_value = fields.Float(string='Quantity')
    user_value_delivered = fields.Float(string='Quantity delivered')
    rental_qty_delivered = fields.Float(string='Rental quantity delivered')

    @api.onchange("order_partner_id")
    def _onchange_scaffold_id(self):
        return {'domain': {'scaffold_id': [('client_id', '=', self.order_partner_id.id)]}}

    @api.onchange('user_value')
    def _onchange_update_user_value(self):
        if self.rental is False:
            self.product_uom_qty = self.user_value

    @api.onchange('user_value_delivered', 'rental_qty_delivered')
    def _onchange_update_qty_delivered(self):
        if self.rental is False:
            self.qty_delivered = self.user_value_delivered
        else:
            self.qty_delivered = self.user_value_delivered * self.rental_qty_delivered

    @api.onchange("start_date", "end_date")
    def _days_amount(self):
        if self.start_date and self.end_date and self.product_id.uom_id in self.env.company.day_udm_ids and self.rental is True:
            dif = (self.end_date - self.start_date).days + 1
            self.product_uom_qty = dif * self.rental_qty
            self.user_value = dif
        elif self.product_id.uom_id not in self.env.company.day_udm_ids:
            if not self.start_date and not self.end_date:
                return
            elif self.start_date and not self.end_date:
                self.end_date = self.start_date
                self.product_uom_qty = 1
                self.user_value = 1
            elif self.end_date and not self.start_date:
                self.start_date = self.end_date
                self.product_uom_qty = 1
                self.user_value = 1
            else:
                dif = (self.end_date - self.start_date).days + 1
                self.product_uom_qty = dif
                self.user_value = dif
