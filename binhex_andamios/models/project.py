from odoo import models, fields, api, _
import calendar
from datetime import timedelta, datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    sequence_id = fields.Many2one(
        string="scaffold sequence",
        comodel_name="ir.sequence"
    )


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _default_timesheet_product_id(self):
        return self.env.ref('sale_timesheet.time_product', False)

    def _get_partner(self):
        return [('client_id', '=', self.partner_id)]

    cubic_meters = fields.Float(related="scaffold_id.cubic_meters", string="Cubic meters")

    assembly_date = fields.Date(related="scaffold_id.assembly_date", readonly=False, string="Assembling date")
    disassembly_date = fields.Date(related="scaffold_id.disassembly_date", readonly=False, string="Disassembly date")

    subscribe_date = fields.Date(related="scaffold_id.subscribe_date", readonly=False, string="Fecha de Alta")
    unsubscribe_date = fields.Date(related="scaffold_id.unsubscribe_date", readonly=False, string="Fecha de Baja")

    renting_start_date = fields.Date(string="Start date")
    renting_end_date = fields.Date(string="End date")

    # applicant = fields.Many2one("res.partner", string="Applicant") #solicitante
    # payer = fields.Many2one("res.partner", string="Payer") #ordenante

    task_name = fields.One2many('scaffold.scaffold', "task_id", string="Task name")
    scaffold_id = fields.Many2one('scaffold.scaffold', string="Scaffold")
    task_type = fields.Selection([
        ('assembly', 'Assembly'),
        ('disassembly', 'Disassembly'),
        ('renting', 'Renting'),
        ('extra', 'Extra'),
    ], string='Task type')

    is_parent = fields.Boolean(default=True)

    # ot_andamio= fields.Char(string="O.T")
    # po_andamio= fields.Char(string="P.O")

    assembly_sub_task = fields.Boolean()
    disassembly_sub_task = fields.Boolean()
    extra_sub_task = fields.Boolean()

    def default_timesheet_product_id(self):
        for record in self:
            if record.timesheet_product_id:
                return record.timesheet_product_id
            if record.scaffold_id:
                if record.task_type == 'assembly' and record.scaffold_id.assembly_prod_id:
                    return record.scaffold_id.assembly_prod_id
                elif record.task_type == 'disassembly' and record.scaffold_id.disassembly_prod_id:
                    return record.scaffold_id.disassembly_prod_id
                elif record.task_type == 'renting' and record.scaffold_id.renting_prod_id:
                    return record.scaffold_id.renting_prod_id
        return self.env.ref('sale_timesheet.time_product', False)

    timesheet_product_id = fields.Many2one(
        'product.product', string='Timesheet Product',
        related='',
        domain="""[
            ('type', '=', 'service')
        ]""",
        readonly=False,
        default=lambda self: self.default_timesheet_product_id()
    )

    worksheet_line_size = fields.Integer()
    hide_create_renting_subtask_button = fields.Boolean(compute="_compute_hide_renting")

    invoiced = fields.Boolean(compute="_compute_invoiced", store=True)

    def _compute_hide_renting(self):
        for task in self:
            last_renting_subtask = task._get_last_renting_subtask()
            if last_renting_subtask and task.unsubscribe_date and last_renting_subtask.renting_end_date >= task.unsubscribe_date:
                task.hide_create_renting_subtask_button = True
            else:
                task.hide_create_renting_subtask_button = False

    def _compute_invoiced(self):
        for task in self:
            task.invoiced = len(self.env['account.move'].search([
                ('cubic_meters_tasks', 'in', task.id),
                ('move_type', '=', "out_invoice"),
                ('state', 'in', ['draft', 'posted']),
                ('payment_state', '!=', 'reversed')])) > 0

    @api.depends('partner_id.commercial_partner_id', 'sale_line_id.order_partner_id.commercial_partner_id', 'parent_id.sale_line_id', 'project_id.sale_line_id')
    def _compute_sale_line(self):
        for task in self:
            if task.is_parent and task.scaffold_id:
                continue
            else:
                super()._compute_sale_line()

    @api.model_create_multi
    def create(self, vals):
        records = self.env['project.task']
        for list in vals:
            record = super().create(list)
            if record.parent_id:
                record.is_parent = False
            if record.scaffold_id and record.is_parent:
                record.scaffold_id.task_id = record.id
            if record.scaffold_id and not record.task_type:
                record._manages_deletion_and_creation_of_subtasks()
            records |= record
        return records

    def write(self, vals):
        super().write(vals)
        for rec in self:
            if rec.is_parent:
                if vals.get('scaffold_id'):
                    rec.scaffold_id.task_id = rec.id
                    for task in rec.child_ids:
                        task.scaffold_id = rec.scaffold_id
                rec._manages_deletion_and_creation_of_subtasks()
                if vals.get('cubic_meters'):
                    for task in self.child_ids:
                        task.write({'cubic_meters': self.cubic_meters})
                if vals.get('timesheet_ids'):
                    if rec.sale_line_id and rec.sale_line_id.product_id.service_policy == 'delivered_timesheet':
                        rec.sale_line_id.user_value_delivered = rec.sale_line_id.qty_delivered
                if vals.get('assembly_date'):
                    for task in self.child_ids:
                        if task.task_type == 'assembly':
                            task.write({'assembly_date': self.assembly_date})
                if vals.get('disassembly_date'):
                    for task in self.child_ids:
                        if task.task_type == 'disassembly':
                            task.write({'disassembly_date': self.disassembly_date})
                for line in rec.timesheet_ids:
                    if not line.owner_task_id:
                        line.owner_task_id = rec.id
            else:
                if vals.get('renting_start_date'):
                    if rec.task_type == 'renting':
                        rec.assembly_date = rec.renting_start_date
                if vals.get('renting_end_date'):
                    if rec.task_type == 'renting':
                        rec.disassembly_date = rec.renting_end_date
            if vals.get('signature'):
                sig_stage = self.env['project.task.type'].search([('sign_stage', '=', rec.id), ('project_ids', '=', rec.project_id.id)], limit=1)
                if sig_stage and not rec.stage_id.is_closed:
                    rec.stage_id = sig_stage.id
        return

    def unlink(self):
        for task in self:
            if task.is_parent and task.scaffold_id:
                task.scaffold_id.task_id = False
        return super().unlink()

    @api.onchange('partner_id')
    def _onchange_partner_id_domain(self):
        return {'domain': {'scaffold_id': [('client_id', '=', self.partner_id.id)]}}

    @api.onchange('timesheet_ids')
    def _set_worksheet_size(self):
        self.worksheet_line_size = len(self.timesheet_ids)

    @api.onchange('scaffold_id')
    def _set_cubic_meters(self):
        self.cubic_meters = self.scaffold_id.cubic_meters

    # If the subtask of that type doesn't exist, it creates it
    def _manages_deletion_and_creation_of_subtasks(self):
        ProjectTaskEnv = self.env['project.task']
        sub_task = ProjectTaskEnv.search([('parent_id', '=', self.id), ('task_type', '=', 'assembly')])
        if self.assembly_sub_task:
            if not sub_task:
                self._create_sub_task('assembly')
        else:
            if sub_task:
                sub_task.unlink()
        sub_task = ProjectTaskEnv.search([('parent_id', '=', self.id), ('task_type', '=', 'disassembly')])
        if self.disassembly_sub_task:
            if not sub_task:
                self._create_sub_task('disassembly')
        else:
            if sub_task:
                sub_task.unlink()
        sub_task = ProjectTaskEnv.search([('parent_id', '=', self.id), ('task_type', '=', 'extra')])
        if self.extra_sub_task:
            if not sub_task:
                self._create_sub_task('extra')
        else:
            if sub_task:
                sub_task.unlink()

    def create_renting_subtask(self):
        self.ensure_one()
        records = self.env['project.task']
        records += self._create_sub_task('renting')
        try:
            for ext in self.scaffold_id.scaffold_extend_ids.mapped('task_id'):
                records += ext._create_sub_task('renting')
        except Exception as e:
            raise UserError(_("%s, in task %s", e, ext.name))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Task'),
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'domain': [['id', 'in', records.ids]],
        }

    def _assembly_params_warning_checking(self):
        if not self.assembly_date:
            raise UserError(_('An assembly date must be set before creating any sub-task'))
        if not self.cubic_meters:
            raise UserError(_('Cubic meters quantity must be set before creating any sub-task'))

    def _disassembly_params_warning_checking(self):
        if not self.disassembly_date:
            raise UserError(_('A disassembly date must be set before creating any sub-task'))
        if not self.cubic_meters:
            raise UserError(_('A disassembly cubic meters must be set before creating any sub-task'))

    def _create_sub_task(self, subtask_type):
        if not self.scaffold_id:
            raise UserError(_('A scaffold must be selected before creating any sub-task'))
        vals = {
            'is_parent': False,
            'scaffold_id' : self.scaffold_id.id,
            'partner_id' : self.partner_id.id,
            # 'partner_email' : self.partner_id.email,
            'project_id' : self.project_id.id,
            'parent_id' : self.id,
            'sale_line_id': False,
        }
        if subtask_type == 'assembly':
            line_assembly_search = self.scaffold_id.assembly_prod_id
            if not line_assembly_search:
                raise UserError(_('There is no selected service that is of type assembly by default'))
            self._assembly_params_warning_checking()
            vals['name'] = self.name + ':' + _('Assembly')
            vals['task_type'] = 'assembly'
            vals['assembly_date'] = self.assembly_date
            vals['cubic_meters'] = self.cubic_meters
            vals['timesheet_product_id'] = line_assembly_search.id
        elif subtask_type == 'disassembly':
            self._disassembly_params_warning_checking()
            line_disassembly_search = self.scaffold_id.disassembly_prod_id
            if not line_disassembly_search:
                raise UserError(_('There is no selected service that is of type disassembly by default'))
            vals['name'] = self.name + ':' + _('Disassembly')
            vals['task_type'] = 'disassembly'
            vals['disassembly_date'] = self.disassembly_date
            vals['cubic_meters'] = self.cubic_meters
            vals['timesheet_product_id'] = line_disassembly_search.id
        elif subtask_type == 'renting':
            self._assembly_params_warning_checking()
            line_renting_search = self.scaffold_id.renting_prod_id
            if not line_renting_search:
                raise UserError(_('There is no selected service that is of type renting by default'))
            start_date = self._get_rent_start_date()
            vals['name'] = self.name + ':' + self._get_renting_subtask_name()
            vals['task_type'] = 'renting'
            vals['renting_start_date'] = start_date.strftime("%Y-%m-%d")
            vals['renting_end_date'] = self._get_rent_end_date(start_date)
            # vals['disassembly_date'] = vals['renting_end_date']
            vals['cubic_meters'] = self.cubic_meters
            vals['timesheet_product_id'] = line_renting_search.id
        elif subtask_type == 'extra':
            vals['name'] = self.name + ':' + _('Extra')
            vals['task_type'] = 'extra'
        return self.env['project.task'].create(vals)

    def _get_last_renting_subtask(self):
        return self.env['project.task'].search([('parent_id', '=', self.id), ('task_type', '=', 'renting')], order='create_date DESC', limit=1)

    def _get_renting_subtask_name(self):
        last_renting_subtask = self._get_last_renting_subtask()
        if last_renting_subtask:
            date = datetime.strptime(str(last_renting_subtask.renting_end_date), "%Y-%m-%d") + timedelta(1)
        else:
            date = datetime.strptime(str(self.assembly_date), "%Y-%m-%d")
        return _("Renting ") + date.strftime("%b")

    def _get_rent_start_date(self):
        last_renting_subtask = self._get_last_renting_subtask()
        if not last_renting_subtask:
            start_date = datetime.combine(self.assembly_date, datetime.min.time())
        else:
            renting_end_date = datetime.combine(last_renting_subtask.renting_end_date, datetime.min.time())
            start_date = renting_end_date + timedelta(1)
        return start_date

    def _get_rent_end_date(self, start_date):
        if not self.unsubscribe_date:
            start_date = start_date + timedelta(1)
            month_end = calendar.monthrange(start_date.year, start_date.month)[1]
            return str(start_date.year) + "-" + str(start_date.month).rjust(2, '0') + "-" + str(month_end).rjust(2, '0')
        else:
            start_date = start_date + timedelta(1)
            if (start_date.month == self.unsubscribe_date.month) and (start_date.year == self.unsubscribe_date.year):
                self.hide_create_renting_subtask_button = True
                return self.unsubscribe_date.strftime("%Y-%m-%d")
            else:
                month_end = calendar.monthrange(start_date.year, start_date.month)[1]
                return str(start_date.year) + "-" + str(start_date.month).rjust(2, '0') + "-" + str(month_end).rjust(2, '0')

    def timesheet_product_price(self, qty=1):
        ts_prod = self.env.ref('sale_timesheet.time_product', False)
        if not ts_prod or not self.scaffold_id:
            return False
        return self.scaffold_id.pricelist_id._get_product_price_rule(ts_prod.id, quantity=qty)[0]


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    sign_stage = fields.Boolean(string="Etapa Firmado")
