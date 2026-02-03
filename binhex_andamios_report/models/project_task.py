from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # supervisor_client = fields.Many2one('res.partner', string="Supervisor client")
    comments = fields.Char(string="Comments")
    signature = fields.Binary('Signature', copy=False)

    def get_right_tariff_price_cubic(self, qty=1):
        if self.scaffold_id and self.timesheet_product_id:
            return self.scaffold_id.pricelist_id._get_product_price_rule(self.timesheet_product_id.id, quantity=qty)[0]
        tariffs = self.env['product.pricelist.item'].search([('product_id', '=', self.timesheet_product_id.id)])
        right_tariff_price = 6
        for tariff in tariffs:
            right_tariff_price = tariff.fixed_price
            if tariff.min_quantity <= self.cubic_meters:
                break
        return right_tariff_price

    def get_right_tariff_price_hours(self, qty=1):
        if self.scaffold_id and self.timesheet_product_id:
            return self.scaffold_id.pricelist_id._get_product_price_rule(self.timesheet_product_id.id, quantity=qty)[0]
        tariffs = self.env['product.pricelist.item'].search([('product_id', '=', self.timesheet_product_id.id)])
        right_tariff_price = 110
        for tariff in tariffs:
            right_tariff_price = tariff.fixed_price
            if tariff.min_quantity <= self.transport_hours:
                break
        return right_tariff_price

    def count_days(self):
        if (not self.assembly_date) or (not self.disassembly_date):
            return 0
        return (self.disassembly_date - self.assembly_date).days + 1

    def total(self):
        total = 0
        for child in self.child_ids:
            if child.cubic_meters and child.task_type in ['assembly', 'dissasembly', 'renting']:
                total += float('%.2f' % (child.get_right_tariff_price_cubic() * float(child.cubic_meters)))
        return total

    def count_days_rent(self):
        if (not self.renting_start_date) and (not self.renting_end_date):
            return 0
        return (self.renting_end_date - self.renting_start_date).days + 1

    def format_date(self, date):
        return date.strftime('%d / %m / %Y')

    def get_timesheets(self):
        timesheets = self.parent_id.timesheet_ids.search([('sub_task', '=', self.id)])
        return timesheets
