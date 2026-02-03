from odoo import models, fields, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        domain=[]
    )

    def action_create_scaffold(self):
        sections = self.env['sale.order.line'].search([('order_id', '=', self.id), ('display_type', '=', 'line_section')])
        scaffold_id = False
        if not sections:
            create_once = True
            for line in self.order_line:
                if line.product_id.product_tmpl_id in self.env.company.scaffold_services and not line.scaffold_id and line.display_type is False:
                    if create_once:
                        _logger.info('OK')
                        name = self.name + '-' + str(len(self.andamio_ids) + 1)
                        scaffold_id = self.env['scaffold.scaffold'].create({
                            'name': name,
                            'client_id': self.partner_id.id,
                            'order_ids': [self.id],
                            'pricelist_id': self.pricelist_id.id,
                            'project_id': self.project_id.id if self.project_id else False
                        })
                        _logger.info('OK2')
                        self.andamio_ids = [(4, scaffold_id.id)]
                        create_once = False
                    line.scaffold_id = scaffold_id
                    if line.product_id.id == self.env.ref('andamios_extend.binhex_normal_hour_operator').id:
                        scaffold_id.write({
                            'normal_hour_price' : line.price_unit
                        })
                        line.scaffold_id = scaffold_id
                    if line.product_id.id == self.env.ref('andamios_extend.binhex_extra_hour_operator').id:
                        scaffold_id.write({
                            'extra_hour_price' : line.price_unit
                        })
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

    def _action_confirm(self):
        if not self.project_id:
            project_id = self.env['project.project'].create({'name': self.name, 'partner_id': self.partner_id.id, 'sale_order_id': self.id})
            self.write({'project_id' : project_id.id})
        return super()._action_confirm()
