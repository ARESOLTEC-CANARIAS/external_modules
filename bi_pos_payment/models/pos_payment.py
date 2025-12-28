# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _
from datetime import datetime


class PaymentNote(models.Model):
    _inherit = 'account.payment'

    notes_pos = fields.Text('Notes')


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name', 'partner_id', 'amount_total', 'amount_residual', 'currency_id', 'state', 'move_type']

    @api.model
    def _load_pos_data_domain(self, data):
        return [['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['payment_state', '!=', 'paid']]

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(
            data['pos.config']['data'][0]['id'])
        return {
            'data': self.search_read(domain, fields, load=False) if domain is not False else [],
            'fields': fields,
        }


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'type']

    @api.model
    def _load_pos_data_domain(self, data):
        return [['type', 'in', ['cash', 'bank']]]

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(
            data['pos.config']['data'][0]['id'])
        return {
            'data': self.search_read(domain, fields, load=False) if domain is not False else [],
            'fields': fields,
        }


class POSOrderLoad(models.Model):
    _inherit = 'pos.session'

    def _load_pos_data_models(self, config_id):
        result = super()._load_pos_data_models(config_id)
        result += ['account.move', 'account.journal']
        return result


class POSConfigPayment(models.Model):
    _inherit = 'pos.config'

    allow_pos_payment = fields.Boolean('Allow POS Payments')
    allow_pos_invoice = fields.Boolean(
        'Allow POS Invoice Payment and Validation')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_pos_payment = fields.Boolean(
        related='pos_config_id.allow_pos_payment', readonly=False)
    allow_pos_invoice = fields.Boolean(
        related='pos_config_id.allow_pos_invoice', readonly=False)


class pos_create_customer_payment(models.Model):
    _name = 'pos.create.customer.payment'
    _description = 'Pos Create Customer Payment'

    def create_customer_payment(self, partner_id, journal, amount, note):
        account_payment_obj = self.env['account.payment']
        values = {
            'payment_type': "inbound",
            'amount': amount,
            'date': datetime.now().date(),
            'journal_id': int(journal),
            'payment_method_id': 1,
            'notes_pos': note,
            'partner_type': 'customer',
            'partner_id': partner_id,
        }
        payment_create = account_payment_obj.sudo().create(values)
        payment_create.action_post()
        return [payment_create.name, payment_create.partner_id.name, payment_create.amount, payment_create.notes_pos]

    def create_customer_payment_inv(self, partner_id, journal, amount, invoice, note):
        payment_object = self.env['account.payment']
        partner_object = self.env['res.partner']
        inv_obj = self.env['account.move'].search(
            [('id', '=', invoice['id'])], limit=1)

        vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': partner_id,
            'journal_id': int(journal),
            'currency_id': inv_obj.currency_id.id,
            'memo': inv_obj.name,
            'notes_pos': note,
            'amount': amount,
            'date': fields.Date.today(),
            'payment_method_id': 1,

        }

        a = payment_object.create(vals)
        a.action_post()

        to_reconcile = []
        to_reconcile.append(inv_obj.line_ids)
        domain = [('account_id.account_type', 'in', ('asset_receivable',
                   'liability_payable')), ('reconciled', '=', False)]
        for payment_object, lines in zip(a, to_reconcile):
            payment_lines = payment_object.move_id.line_ids.filtered_domain(
                domain)
            for account in payment_lines.account_id:
                (payment_lines + lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()
        return [a.name, a.partner_id.name, a.amount, a.notes_pos]
