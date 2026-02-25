from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class Andamios(models.Model):
    _name = 'scaffold.scaffold'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = "create_date desc"

    def _default_assembly(self):
        default_assembly_search = self.env['product.product'].search([
            ('default_service', '=', 'assembly')
        ], limit=1)
        _logger.info('OK1 %s' % default_assembly_search)
        if default_assembly_search:
            return default_assembly_search
        else:
            default_assembly_search = self.env['product.template'].search([
                ('scaffold_service_type', '=', 'assembly')
            ], limit=1).product_variant_id
            _logger.info('OK2 %s' % default_assembly_search)
            if default_assembly_search:
                return default_assembly_search
            raise UserError(_('There is no selected service that is of type assembly by default'))

    def _default_disassembly(self):
        default_disassembly_search = self.env['product.product'].search([
            ('default_service', '=', 'disassembly')
        ], limit=1)
        if default_disassembly_search:
            return default_disassembly_search
        else:
            default_disassembly_search = self.env['product.template'].search([
                ('scaffold_service_type', '=', 'disassembly')
            ], limit=1).product_variant_id
            if default_disassembly_search:
                return default_disassembly_search
            raise UserError(_('There is no selected service that is of type assembly by default'))

    def _default_renting(self):
        default_renting_search = self.env['product.product'].search([
            ('default_service', '=', 'renting')
        ], limit=1)
        if default_renting_search:
            return default_renting_search
        else:
            default_renting_search = self.env['product.template'].search([
                ('scaffold_service_type', '=', 'renting')
            ], limit=1).product_variant_id
            if default_renting_search:
                return default_renting_search
            raise UserError(_('There is no selected service that is of type assembly by default'))

    def _default_extension(self):
        default_extension_search = self.env['product.product'].search([
            ('default_service', '=', 'extension')
        ], limit=1)
        if default_extension_search:
            return default_extension_search
        else:
            default_extension_search = self.env['product.template'].search([
                ('scaffold_service_type', '=', 'extension')
            ], limit=1).product_variant_id
            if default_extension_search:
                return default_extension_search
            raise UserError(_('There is no selected service that is of type extension by default'))

    name = fields.Char(string='Name', copy=False)
    client_id = fields.Many2one("res.partner",
                                ondelete="restrict",
                                string="Client",
                                domain=[('parent_id', '=', False)],
                                required=True)
    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")
    order_ids = fields.Many2many(
        "sale.order",
        "sale_order_andamio",
        "id1",
        "id2",
        ondelete="restrict",
        string="Sale order",
        readonly=True,
        copy=False
    )
    task_id = fields.Many2one(
        "project.task",
        domain="[('is_parent','=',True),('scaffold_id','=',id)]",
        ondelete="restrict",
        string="Worksheet",
        copy=False
    )
    sequence = fields.Integer('Sequence')
    contact_id = fields.Many2one("res.partner", ondelete="restrict", string="Contact")
    contact_email = fields.Char(string="Email")
    contact_phone = fields.Char(string="Telephone number")
    image = fields.Binary(string="Image")
    account_move_ids = fields.Many2many("account.move", string="Invoices", readonly=True, copy=False)
    andamio_conteo = fields.Integer(string="Scaffold", compute="get_count")
    height = fields.Float(string="Height")
    llength = fields.Float(string="Length")
    width = fields.Float(string="Width")
    cubic_meters = fields.Float(string="Cubic meters", compute="_compute_m3", readonly=True)
    add_modules = fields.Float(string="Extensions", compute="_compute_extens")
    addit_modules = fields.Float(string="Additional Modules")
    image = fields.Binary()
    location = fields.Char(string="Location")
    zone = fields.Many2one("scaffold.zone", string="Zone")
    assembly_prod_id = fields.Many2one(
        "product.product",
        required=True,
        string="Assembly service",
        domain=[("product_tmpl_id.scaffold_service_type", "=", "assembly")],
        default=_default_assembly
    )
    disassembly_prod_id = fields.Many2one(
        "product.product",
        required=True,
        string="Disassembly service",
        domain=[("product_tmpl_id.scaffold_service_type", "=", "disassembly")],
        default=_default_disassembly
    )
    renting_prod_id = fields.Many2one(
        "product.product",
        required=True,
        string="Renting service",
        domain=[("product_tmpl_id.scaffold_service_type", "=", "renting")],
        default=_default_renting
    )
    extension_prod_id = fields.Many2one(
        "product.product",
        required=True,
        string="Extension service",
        domain=[("product_tmpl_id.scaffold_service_type", "=", "extension")],
        default=_default_extension
    )
    stage_id = fields.Many2one("scaffold.stage", string="Stage")
    fast_task = fields.Boolean(string="Create subtask")
    supervisor_id = fields.Many2one(
        string="Supervisor",
        comodel_name='res.users',
        ondelete='restrict',
    )

    # Manage hierarchy
    parent_id = fields.Many2one("scaffold.scaffold", string="Parent")
    is_extension = fields.Boolean()
    scaffold_extend_ids = fields.One2many(
        "scaffold.scaffold",
        "parent_id",
        domain="[('parent_id','=',id)]",
        string="Extensions",
        copy=False,
        ondelete="cascade"
    )

    task_count = fields.Integer("Tasks", compute="_compute_task_count")
    sales_order_count = fields.Integer("Sale Orders", compute="_compute_sales_order_count")
    invoice_count = fields.Integer("Invoices", compute="_compute_invoice_count")

    # Fields from task
    applicant = fields.Many2one("res.partner", string="Applicant")  # solicitante
    payer = fields.Many2one("res.partner", string="Payer")  # ordenante
    ot_andamio = fields.Char(string="O.T")
    po_andamio = fields.Char(string="P.O")

    supervisor_client = fields.Many2one('res.partner', string="Supervisor client")

    description = fields.Text(string="Description")

    @api.constrains('assembly_date', 'subscribe_date', 'unsubscribe_date', 'disassembly_date')
    def _check_dates(self):
        for scaffold in self:
            if not scaffold.assembly_date and any([scaffold.subscribe_date, scaffold.unsubscribe_date, scaffold.disassembly_date]):
                raise ValidationError(_('Fecha de montaje no establecida'))
            if not scaffold.subscribe_date and any([scaffold.unsubscribe_date, scaffold.disassembly_date]):
                raise ValidationError(_('Fecha de alta no establecida'))
            if not scaffold.unsubscribe_date and scaffold.disassembly_date:
                raise ValidationError(_('Fecha de baja no establecida'))

            if scaffold.assembly_date and scaffold.subscribe_date and scaffold.assembly_date > scaffold.subscribe_date:
                raise ValidationError(_('La fecha de montaje no puede ser posterior a la de alta'))
            if scaffold.subscribe_date and scaffold.unsubscribe_date and scaffold.subscribe_date > scaffold.unsubscribe_date:
                raise ValidationError(_('La fecha de alta no puede ser posterior a la de baja'))
            if scaffold.unsubscribe_date and scaffold.disassembly_date and scaffold.unsubscribe_date > scaffold.disassembly_date:
                raise ValidationError(_('La fecha de baja no puede ser posterior a la de desmontaje'))

    # dates
    assembly_date = fields.Date(string="Assembling date")
    disassembly_date = fields.Date(string="Disassembly date")

    subscribe_date = fields.Date(string="Fecha de Alta")
    unsubscribe_date = fields.Date(string="Fecha de Baja")

    project_id = fields.Many2one(comodel_name="project.project", string="Project")

    def _compute_sales_order_count(self):
        for task in self:
            task.sales_order_count = len(task.order_ids.ids)

    def _compute_invoice_count(self):
        for task in self:
            task.invoice_count = len(task.account_move_ids.ids)

    def _compute_task_count(self):
        for task in self:
            task.task_count = len(task.task_id.ids)

    @api.onchange('client_id')
    def _client_change(self):
        for scaf in self:
            scaf.pricelist_id = scaf.client_id.property_product_pricelist.id

    @api.depends('height', 'llength', 'width', 'addit_modules')
    def _compute_m3(self):
        for scaf in self:
            scaf.cubic_meters = scaf.height * scaf.llength * scaf.width + scaf.addit_modules

    @api.depends('scaffold_extend_ids')
    def _compute_extens(self):
        for scaf in self:
            scaf.add_modules = 0
            for extn in scaf.scaffold_extend_ids:
                scaf.add_modules += extn.cubic_meters

    def write(self, vals):
        project_id = vals.get('project_id', False)
        if project_id:
            vals['name'] = self._get_sequence_number(self.env['project.project'].browse(project_id))
        super(Andamios, self).write(vals)
        for scaf in self:
            if vals.get('pricelist_id', False) and not scaf.is_extension:
                scaf.scaffold_extend_ids.write({'pricelist_id': scaf.pricelist_id})
            if vals.get('assembly_prod_id', False) and scaf.task_id:
                scaf.task_id.child_ids \
                    .filtered(lambda x: x.task_type == 'assembly') \
                    .write({'timesheet_product_id': vals.get('assembly_prod_id')})
            if vals.get('disassembly_prod_id', False) and scaf.task_id:
                scaf.task_id.child_ids \
                    .filtered(lambda x: x.task_type == 'disassembly') \
                    .write({'timesheet_product_id': vals.get('disassembly_prod_id')})
            if vals.get('renting_prod_id', False) and scaf.task_id:
                scaf.task_id.child_ids \
                    .filtered(lambda x: x.task_type == 'renting') \
                    .write({'timesheet_product_id': vals.get('renting_prod_id')})

    @api.model
    def _get_sequence_number(self, project=False):
        if project and project.sequence_id:
            return project.sequence_id.next_by_id()
        return self.env['ir.sequence'].next_by_code('scaffold.scaffold')

    @api.model_create_multi
    def create(self, vals):
        for list in vals:
            project_id = list.get('project_id', False)
            if project_id:
                list['name'] = self._get_sequence_number(self.env['project.project'].browse(project_id))
            if not list.get('client_id') and list.get('parent_id'):
                list['client_id'] = self.browse([list.get('parent_id')]).client_id.id
            record = super(Andamios, self).create(list)
            if record.order_ids:
                record.client_id = record.order_ids[0].partner_id
            if self._context.get('partner_id'):
                record.client_id = self._context.get('partner_id')
            if record.parent_id and not record.parent_id.task_id and not record.parent_id.task_id.project_id:
                raise ValidationError(_("Parent scaffold must be assigned to some task/project"))
            if record.parent_id:
                record.pricelist_id = record.parent_id.pricelist_id
                record.client_id = record.parent_id.client_id
                self.env['project.task'].create({
                    'name' : record.name + " (Ext)",
                    'scaffold_id' : record.id,
                    'partner_id' : record.client_id.id,
                    # 'partner_email' : record.client_id.email,
                    'project_id' : record.parent_id.task_id.project_id.id,
                    'sale_line_id': False,
                })

        return record

    def get_count(self):
        count = self.env['scaffold.scaffold'].search_count([('name', '=', self.id)])
        self.andamio_conteo = count

    def create_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'context': {
                'scaffold_id': self.id,
                'default_partner_id': self.client_id.id,
                'default_partner_invoice_id': self.client_id.id,
                'default_partner_shipping_id': self.client_id.id,
                'default_date_order': datetime.now(),
                'default_pricelist_id': self.pricelist_id.id,
                'default_andamio_ids': [(6, 0, [self.id])],
                'default_order_line': self._create_order_line_by_scaffold(),
            },
        }

    def create_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'target': 'current',
            'context': {
                'default_move_type': 'out_invoice',
                'default_partner_id': self.client_id.id,
                'default_boolean_task': True,
                'scaffold_ref_id': self.id,
                'default_project_id': self.task_id.project_id.id,
                'project_ref_id': self.task_id.project_id.id
            }
        }

    def create_task(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.task',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_scaffold_id': self.id,
                'default_project_id': self.project_id.id,
                'default_user_id' : self.supervisor_id.id,
                'default_partner_id': self.client_id.id,
                'default_description': self.description
            }
        }

    def _create_order_line_by_scaffold(self):
        actual_time = datetime.today()

        if not self.assembly_prod_id:
            raise UserError(_('The scaffold doesn\'t have any assembly service selected'))
        if not self.disassembly_prod_id:
            raise UserError(_('The scaffold doesn\'t have any disassembly service selected'))
        if not self.renting_prod_id:
            raise UserError(_('The scaffold doesn\'t have any renting service selected'))

        order_lines = []
        order_lines += [[0, 0, {
            'product_id' : self.assembly_prod_id.id,
            'product_uom' : self.assembly_prod_id.uom_id.id,
            'scaffold_id' : self.id,
            'name' : self.assembly_prod_id.name,
            'start_date' : False,
            'end_date' : False,
            'task_type' : 'assembly',
            'user_value': 1,
            'product_uom_qty': 1,
        }]]
        order_lines += [[0, 0, {
            'product_id' : self.disassembly_prod_id.id,
            'product_uom' : self.disassembly_prod_id.uom_id.id,
            'scaffold_id' : self.id,
            'name' : self.disassembly_prod_id.name,
            'start_date' : False,
            'end_date' : False,
            'task_type' : 'disassembly',
            'user_value': 1,
            'product_uom_qty': 1,
        }]]
        order_lines += [[0, 0, {
            'product_id' : self.renting_prod_id.id,
            'product_uom' : self.renting_prod_id.uom_id.id,
            'scaffold_id' : self.id,
            'name' : self.renting_prod_id.name,
            'start_date' : actual_time.strftime('%Y-%m-%d'),
            'end_date' : actual_time.strftime('%Y-%m-%d'),
            'task_type' : 'renting',
            'user_value': 1,
            'product_uom_qty': 1,
        }]]

        if self.env.ref("sale_timesheet.time_product"):
            product = self.env.ref("sale_timesheet.time_product")
            order_lines += [[0, 0, {
                'product_id' : product.id,
                'product_uom' : product.uom_id.id,
                'scaffold_id' : self.id,
                'name' : product.name,
                'start_date' : actual_time.strftime('%Y-%m-%d'),
                'end_date' : actual_time.strftime('%Y-%m-%d'),
                'user_value': 1,
                'product_uom_qty': 1,
            }]]

        return order_lines

    def preview_project(self):
        return {
            'name': self.name + _('Project'),
            'view_mode': 'form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'res_id': self.task_id.project_id.id,
            'target': 'current',
        }

    def action_view_tasks(self):
        return {
            'name': self.name + _(' Tasks'),
            'view_mode': 'kanban,list,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.task_id.id)],
            'target': 'current',
        }

    def action_view_sale_orders(self):
        return {
            'name': self.name + _(' Sale Orders'),
            'view_mode': 'list,kanban,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.order_ids.ids)],
            'target': 'current',
        }

    def action_view_invoices(self):
        return {
            'name': self.name + _(' Invoices'),
            'view_mode': 'list,kanban,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.account_move_ids.ids)],
            'target': 'current',
        }

    @api.model
    def check_scaffold_stage(self):
        today = fields.Date.today()

        for scaf in self.search([
            ('task_id', '!=', False),
            ('stage_id', '=', False)
        ]).filtered(
            lambda scf: scf.task_id.assembly_date
            and scf.task_id.assembly_date <= today
            and self.env["mail.activity"].search_count([("res_id", "=", scf.id), ("res_model", "=", self._name)]) == 0
        ):
            scaf.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=scaf.task_id.activity_user_id.id,
                note=_("Basado en la Fecha de montaje este andamio debería estar en la etapa Montaje"))

        for scaf in self.search([
            ('task_id', '!=', False),
            ('stage_id', '=', self.env.ref('binhex_andamios.stage_montaje').id)
        ]).filtered(
            lambda scf: scf.task_id.subscribe_date
            and scf.task_id.subscribe_date <= today
            and self.env["mail.activity"].search_count([("res_id", "=", scf.id), ("res_model", "=", self._name)]) == 0
        ):
            scaf.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=scaf.task_id.activity_user_id.id,
                note=_("Basado en la Fecha de alta este andamio debería estar en la etapa Alta"))

        for scaf in self.search([
            ('task_id', '!=', False),
            ('stage_id', '=', self.env.ref('binhex_andamios.stage_alta').id)
        ]).filtered(
            lambda scf: scf.task_id.unsubscribe_date
            and scf.task_id.unsubscribe_date <= today
            and self.env["mail.activity"].search_count([("res_id", "=", scf.id), ("res_model", "=", self._name)]) == 0
        ):
            scaf.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=scaf.task_id.activity_user_id.id,
                note=_("Basado en la Fecha de baja este andamio debería estar en la etapa Baja"))

        for scaf in self.search([('task_id', '!=', False), ('stage_id', '=', self.env.ref('binhex_andamios.stage_baja').id)]) \
            .filtered(lambda scf: scf.task_id.disassembly_date and scf.task_id.disassembly_date <= today
                      and self.env["mail.activity"].search_count([("res_id", "=", scf.id), ("res_model", "=", self._name)]) == 0):
            scaf.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=scaf.task_id.activity_user_id.id,
                note=_("Basado en la Fecha de desmontaje este andamio debería estar en la etapa Desmontaje"))
