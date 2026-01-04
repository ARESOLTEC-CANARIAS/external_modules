# Copyright (C) 2017-2021 Creu Blanca
# Copyright (C) 2024 Tecnativa <https://tecnativa.com>
# Copyright (C) 2024 Servincom Soluciones
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError

ALLOWED_TYPES = {
    "customer": ["out_invoice", "in_refund"],
    "vendor": ["in_invoice", "out_refund"],
}


class CashPayInvoice(models.TransientModel):
    _name = "cash.pay.invoice"
    _description = "Cash Pay invoice from bank statement"

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        required=True,
        compute="_compute_invoice_id",
        store=True,
        readonly=False,
    )
    name = fields.Char(related="invoice_id.name", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company", compute="_compute_company_id"
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", compute="_compute_currency_id"
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        required=True,
        domain="[('type', 'in', ['bank', 'cash'])]",
        string="Journal",
    )
    amount = fields.Monetary(compute="_compute_amount", store=True, readonly=False)
    invoice_type = fields.Selection(
        [
            ("customer", "Customer"),
            ("vendor", "Vendor"),
        ],
    )
    invoice_domain = fields.Binary(compute="_compute_invoice_domain")

    @api.depends("journal_id")
    def _compute_company_id(self):
        for record in self:
            record.company_id = record.journal_id.company_id

    @api.depends("journal_id")
    def _compute_currency_id(self):
        for record in self:
            journal = record.journal_id
            record.currency_id = journal.currency_id or journal.company_id.currency_id

    @api.depends("company_id", "currency_id", "invoice_type")
    def _compute_invoice_domain(self):
        for wizard in self:
            invoice_domain = [
                ("company_id", "=", wizard.company_id.id),
                ("currency_id", "=", wizard.currency_id.id),
                ("state", "=", "posted"),
                ("payment_state", "!=", "paid"),
            ]
            move_types = ALLOWED_TYPES.get(wizard.invoice_type, [])
            invoice_domain.append(("move_type", "in", move_types))
            wizard.invoice_domain = invoice_domain

    @api.depends("invoice_type")
    def _compute_invoice_id(self):
        for wizard in self:
            allowed = ALLOWED_TYPES.get(wizard.invoice_type, [])
            if wizard.invoice_id.move_type and wizard.invoice_id.move_type not in allowed:
                wizard.invoice_id = False

    @api.depends("invoice_id")
    def _compute_amount(self):
        for wizard in self:
            wizard.amount = wizard.invoice_id.amount_residual_signed

    def action_pay_invoice(self):
        self.ensure_one()

        BankStatementLine = self.env["account.bank.statement.line"]
        statement_line_vals = self._prepare_statement_line_vals()
        new_statement_line = BankStatementLine.create(statement_line_vals)

        lines_to_reconcile = (
            new_statement_line.invoice_id.line_ids | new_statement_line.move_id.line_ids
        ).filtered(
            lambda l: l.account_id.account_type
            in ("asset_receivable", "liability_payable")
            and not l.reconciled
        )
        lines_to_reconcile.reconcile()

        return {"type": "ir.actions.act_window_close"}

    def _prepare_statement_line_vals(self):
        self.ensure_one()

        counterpart_lines = self.invoice_id.line_ids.filtered(
            lambda l: l.account_id.account_type
            in ("asset_receivable", "liability_payable")
            and not l.reconciled
        )
        if not counterpart_lines:
            raise UserError("No hay línea pendiente a conciliar (a cobrar/pagar) en la factura.")

        statement_line_vals = {
            "date": fields.Date.context_today(self),
            "journal_id": self.journal_id.id,
            "company_id": self.company_id.id,
            "amount": self.amount,
            "payment_ref": self.name,
            "invoice_id": self.invoice_id.id,
            "ref": self.invoice_id.name,
            "partner_id": self.invoice_id.partner_id.id,
            "counterpart_account_id": counterpart_lines[:1].account_id.id,
        }
        return statement_line_vals
