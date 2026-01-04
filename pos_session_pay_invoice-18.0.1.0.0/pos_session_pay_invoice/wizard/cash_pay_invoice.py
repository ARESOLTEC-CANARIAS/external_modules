# Copyright (C) 2017-2021 Creu Blanca
# Copyright (C) 2024 Tecnativa <https://tecnativa.com>
# Copyright (C) 2026 Servincom Soluciones
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

# OJO: este mapping es por "dirección del dinero" (cobro vs pago), no por "tipo de partner".
ALLOWED_TYPES = {
    "customer": ["out_invoice", "in_refund"],  # cobros (cliente factura / proveedor abono)
    "vendor": ["in_invoice", "out_refund"],    # pagos (proveedor factura / cliente abono)
}


class CashPayInvoice(models.TransientModel):
    _inherit = "cash.pay.invoice"

    pos_order_id = fields.Many2one(
        comodel_name="pos.order",
        string="POS Order",
        readonly=True,
    )

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="POS Session",
        readonly=True,
    )

    pos_payment_method_id = fields.Many2one(
        comodel_name="pos.payment.method",
        string="POS Payment Method",
        required=True,
    )

    pos_payment_method_domain = fields.Binary(
        compute="_compute_pos_payment_method_domain",
    )

    # -------------------------
    # Defaults / Onchange
    # -------------------------

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        # Traer sesión desde contexto si viene (lo normal en tu botón desde pos.session)
        session_id = self.env.context.get("default_pos_session_id")
        if session_id and "pos_session_id" in fields_list:
            res["pos_session_id"] = session_id

        # Si ya viene el método de pago por defecto, setear journal_id coherente
        pm_id = res.get("pos_payment_method_id") or self.env.context.get("default_pos_payment_method_id")
        if pm_id:
            pm = self.env["pos.payment.method"].browse(pm_id)
            if pm and pm.journal_id:
                res["journal_id"] = pm.journal_id.id

        return res

    @api.onchange("pos_payment_method_id")
    def _onchange_pos_payment_method_id(self):
        """
        El wizard base usa journal_id para derivar:
        - company_id
        - currency_id
        - invoice_domain
        Así que aquí lo sincronizamos SIEMPRE desde el método de pago del POS.
        """
        for wizard in self:
            wizard.journal_id = wizard.pos_payment_method_id.journal_id

    # -------------------------
    # Domain de facturas (CORRECCIÓN)
    # -------------------------

    @api.depends("company_id", "currency_id", "invoice_type")
    def _compute_invoice_domain(self):
        """
        Si el wizard se abre desde el POS, forzamos el tipo de factura a mostrar
        usando el contexto 'pos_pay_invoice_domain' (out_invoice, out_refund, in_invoice, etc.).
        """
        super()._compute_invoice_domain()
        forced_move_type = self.env.context.get("pos_pay_invoice_domain")
        if not forced_move_type:
            return

        for wizard in self:
            domain = wizard.invoice_domain or []
            # eliminar cualquier filtro previo sobre move_type
            domain = [
                d for d in domain
                if not (isinstance(d, (list, tuple)) and len(d) >= 3 and d[0] == "move_type")
            ]
            domain.append(("move_type", "=", forced_move_type))
            wizard.invoice_domain = domain

    # -------------------------
    # Domains POS payment methods
    # -------------------------

    @api.depends("pos_session_id", "invoice_type")
    @api.depends_context("default_pos_session_id")
    def _compute_pos_payment_method_domain(self):
        for wizard in self:
            session = wizard.pos_session_id
            if not session:
                session_id = wizard.env.context.get("default_pos_session_id")
                session = wizard.env["pos.session"].browse(session_id) if session_id else wizard.env["pos.session"]

            # En Odoo 18 normalmente están en session.payment_method_ids (si no, caemos a config)
            payment_methods = getattr(session, "payment_method_ids", False) or session.config_id.payment_method_ids

            wizard.pos_payment_method_domain = [("id", "in", payment_methods.ids)]

    # -------------------------
    # Helpers
    # -------------------------

    def _get_invoice_payment_product(self):
        """
        Creamos/buscamos un producto servicio para meter 1 línea en el pos.order
        y que el total del pedido sea EXACTAMENTE el importe del pago.
        """
        Product = self.env["product.product"]

        product = self.env.ref(
            "pos_session_pay_invoice.product_invoice_payment",
            raise_if_not_found=False
        )
        if product:
            return product

        product = Product.search([("default_code", "=", "POS_INV_PAY")], limit=1)
        if product:
            return product

        return Product.create({
            "name": "Pago de factura POS",
            "default_code": "POS_INV_PAY",
            "detailed_type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "available_in_pos": True,
            "list_price": 0.0,
            "taxes_id": [(6, 0, [])],
        })

    def _prepare_pos_order_vals(self):
        self.ensure_one()

        if not self.pos_session_id:
            raise UserError(_("No POS session provided."))

        if not self.pos_payment_method_id:
            raise UserError(_("No POS payment method selected."))

        if not self.invoice_id:
            raise UserError(_("No invoice selected."))

        pay_product = self._get_invoice_payment_product()

        config = self.pos_session_id.config_id
        pricelist = config.pricelist_id or config.available_pricelist_ids[:1]
        if not pricelist:
            raise UserError(_("No pricelist configured on the POS."))

        return {
            "session_id": self.pos_session_id.id,
            "company_id": self.pos_session_id.company_id.id,
            "partner_id": self.invoice_id.partner_id.id,
            "pricelist_id": pricelist.id,

            # En Odoo 18 POS: el campo del pedido es account_move (Many2one a account.move)
            "account_move": self.invoice_id.id,

            "lines": [(0, 0, {
                "product_id": pay_product.id,
                "name": pay_product.display_name,
                "qty": 1,
                "price_unit": self.amount,
                "discount": 0,
                "tax_ids": [(6, 0, [])],
            })],
        }

    def _prepare_pos_payment_vals(self):
        self.ensure_one()
        return {
            "payment_method_id": self.pos_payment_method_id.id,
            "amount": self.amount,
            "payment_date": fields.Datetime.now(),
        }

    def _prepare_statement_line_vals(self):
        """
        Para el flujo "no POS order" (proveedores, etc.), reutilizamos el wizard base
        que crea account.bank.statement.line + reconcile, pero si existe el campo
        pos_session_id en statement line, lo rellenamos para que quede ligado.
        """
        vals = super()._prepare_statement_line_vals()
        if self.pos_session_id:
            BankStatementLine = self.env["account.bank.statement.line"]
            if "pos_session_id" in BankStatementLine._fields:
                vals["pos_session_id"] = self.pos_session_id.id
        return vals

    # -------------------------
    # Action principal
    # -------------------------

    def action_pay_invoice(self):
        """
        Flujo:
        - Si es documento de cliente (out_invoice / out_refund): crear pos.order + pos.payment y aplicar pagos POS.
        - Para el resto (p.ej. in_invoice): usar flujo base (bank statement line + reconcile).
        """
        self.ensure_one()

        if not self.invoice_id:
            raise UserError(_("No invoice selected."))

        # Asegurar journal_id coherente (para company/currency/domains del wizard base)
        if self.pos_payment_method_id and self.pos_payment_method_id.journal_id:
            self.journal_id = self.pos_payment_method_id.journal_id

        move_type = self.invoice_id.move_type

        if move_type in ("out_invoice", "out_refund"):
            pos_order = self.env["pos.order"].create(self._prepare_pos_order_vals())
            pos_order.add_payment(self._prepare_pos_payment_vals())

            if hasattr(pos_order, "action_pos_order_paid"):
                pos_order.action_pos_order_paid()
            else:
                pos_order.write({"state": "paid"})

            # Lógica estándar de Odoo 18 (point_of_sale) para aplicar pagos a la factura
            pos_order._apply_invoice_payments(pos_order.session_id.state == "closed")

            self.pos_order_id = pos_order.id
            return {"type": "ir.actions.act_window_close"}

        # Resto de casos: dejamos que el wizard base cree statement line + reconcile
        super().action_pay_invoice()
        return {"type": "ir.actions.act_window_close"}
