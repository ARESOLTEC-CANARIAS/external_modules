from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    sequence_id = fields.Many2one(
        string="scaffold sequence",
        comodel_name="ir.sequence"
    )


class ProjectTask(models.Model):
    _inherit = "project.task"

    material_total = fields.Monetary(string='Total', compute="_compute_material_total")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id)
    task_type = fields.Selection(selection_add=[('partial', 'Partial')])
    partial_task_ids = fields.Many2many('project.task', 'partial_task_rel', 'task_id', 'partial_task_id')
    facture_in_partial = fields.Boolean(string='Facture in partial', default=False)
    description = fields.Html(string='description', translate=True)
    create_all_renting = fields.Boolean(string='Create all renting')
    date_deadline = fields.Datetime(default=fields.Date.today())
    custom_timesheet_ids = fields.One2many(
        comodel_name="project.task.time",
        inverse_name="task_id",
        string="Timesheet"
    )

    normal_subtotal_hours = fields.Float(compute="_compute_total_hours")
    extra_subtotal_hours = fields.Float(compute="_compute_total_hours")
    total_hours = fields.Float(compute="_compute_total_hours")
    activity_user_id = fields.Many2one(readonly=False, store=True)

    @api.depends('activity_ids.user_id', 'scaffold_id', 'scaffold_id.supervisor_id')
    def _compute_activity_user_id(self):
        for record in self:
            if record.scaffold_id:
                record.activity_user_id = record.scaffold_id.supervisor_id
            else:
                record.activity_user_id = record.activity_ids[0].user_id if record.activity_ids else False

    def _compute_total_hours(self):
        for record in self:
            normal = sum(record.custom_timesheet_ids.filtered(
                lambda ts : ts.type_hour == 'normal'
            ).mapped('unit_amount'))
            extra = sum(record.custom_timesheet_ids.filtered(
                lambda ts : ts.type_hour == 'extra'
            ).mapped('unit_amount'))

            record.normal_subtotal_hours = normal
            record.extra_subtotal_hours = extra
            record.total_hours = normal + extra
            record.effective_hours = record.total_hours

    def _compute_material_total(self):
        for record in self:
            record.material_total = sum(record.material_ids.mapped('price_subtotal'))

    def get_right_tariff_price_cubic(self):
        if self.task_type == "assembly":
            return self.scaffold_id.assembly_price
        if self.task_type == "disassembly":
            return self.scaffold_id.disassembly_price
        if self.task_type == "renting":
            return self.scaffold_id.renting_price

        return super().get_right_tariff_price_cubic()

    def get_timesheets_for_report(self):
        timesheet_data = []
        timesheet_ids = self.custom_timesheet_ids
        if timesheet_ids:
            employee_ids = timesheet_ids.mapped('employee_id')
            subtask_ids = timesheet_ids.mapped('subtask_id')
            for employee_id in employee_ids:
                for subtask_id in subtask_ids:
                    normal_hours = sum(timesheet_ids.filtered(
                        lambda line: (line.employee_id.id == employee_id.id and
                                      line.subtask_id.id == subtask_id.id and
                                      line.type_hour == "normal")).mapped('unit_amount'))
                    extra_hours = sum(timesheet_ids.filtered(
                        lambda line: (line.employee_id.id == employee_id.id and
                                      line.subtask_id.id == subtask_id.id and
                                      line.type_hour == "extra")).mapped('unit_amount'))
                    total = sum([
                        normal_hours * self.scaffold_id.normal_hour_price,
                        extra_hours * self.scaffold_id.extra_hour_price
                    ])

                    if total == 0:
                        continue

                    timesheet_data.append({
                        'name': employee_id.name,
                        'subtask': subtask_id,
                        'normal_hour': normal_hours,
                        'extra_hour': extra_hours,
                        'normal_hour_price': self.scaffold_id.normal_hour_price,
                        'extra_hour_price': self.scaffold_id.extra_hour_price,
                        'total': total
                    })
        return timesheet_data

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

    def _get_renting_subtask_name(self):
        last_renting_subtask = self._get_last_renting_subtask()
        if last_renting_subtask:
            date = datetime.strptime(str(last_renting_subtask.renting_end_date), "%Y-%m-%d") + timedelta(1)
        else:
            date = datetime.strptime(str(self.subscribe_date), "%Y-%m-%d")
        if self.create_all_renting:
            return _("Renting ")

        return _("Renting ") + date.strftime("%b")

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
            vals['cubic_meters'] = self.cubic_meters
            vals['timesheet_product_id'] = line_renting_search.id
        elif subtask_type == 'extra':
            vals['name'] = self.name + ':' + _('Extra')
            vals['task_type'] = 'extra'
        return self.env['project.task'].create(vals)

    def action_generate_partial_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Partial Task'),
            'res_model': 'scaffold.partial.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_scaffold_id': self.scaffold_id.id,
                'default_task_id': self.id,
            }
        }

    @api.onchange('assembly_date')
    def _on_change_assembly_date(self):
        for record in self:
            if record.assembly_date:
                record.scaffold_id.write({
                    'stage_id' : self.env.ref('binhex_andamios.stage_montaje').id
                })

    @api.onchange('subscribe_date')
    def _on_change_subscribe_date(self):
        for record in self:
            if record.subscribe_date:
                record.scaffold_id.write({
                    'stage_id' : self.env.ref('binhex_andamios.stage_alta').id
                })

    @api.onchange('unsubscribe_date')
    def _on_change_unsubscribe_date(self):
        for record in self:
            if record.unsubscribe_date:
                record.scaffold_id.write({
                    'stage_id' : self.env.ref('binhex_andamios.stage_baja').id
                })

    @api.onchange('disassembly_date')
    def _on_change_disassembly_date(self):
        for record in self:
            if record.disassembly_date:
                record.scaffold_id.write({
                    'stage_id' : self.env.ref('binhex_andamios.stage_desmontaje').id
                })

    def action_subtask(self):
        res = super().action_subtask()
        res['domain'] = [('id', 'child_of', self.id), ('id', '!=', self.id), ('facture_in_partial', '=', False)]
        return res

    @api.depends('child_ids')
    def _compute_subtask_count(self):
        super()._compute_subtask_count()
        for task in self:
            task.subtask_count = len(task._get_all_subtasks().filtered(lambda task: task.facture_in_partial is False))

    def _get_rent_start_date(self):
        last_renting_subtask = self._get_last_renting_subtask()
        if not last_renting_subtask:
            start_date = datetime.combine(self.subscribe_date, datetime.min.time())
        else:
            renting_end_date = datetime.combine(last_renting_subtask.renting_end_date, datetime.min.time())
            start_date = renting_end_date + timedelta(1)
        return start_date

    def _get_rent_end_date(self, start_date):
        res = super()._get_rent_end_date(start_date)
        if self.unsubscribe_date and self.create_all_renting:
            return self.unsubscribe_date.strftime("%Y-%m-%d")
        return res

    def action_cancelled_partial_task(self):
        self.partial_task_ids.write({'facture_in_partial': False})
        self.write({
            'stage_id' : self.env.ref('project_task_default_stage.project_tt_cancel').id
        })
