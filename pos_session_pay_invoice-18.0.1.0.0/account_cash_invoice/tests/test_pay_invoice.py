# Copyright 2017-2021 Creu Blanca <https://creublanca.es/>
# Copyright (C) 2024 Tecnativa <https://tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSessionPayInvoice(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.AccountMove = cls.env["account.move"]

        # Partner sin depender de demo data
        cls.partner = cls.env["res.partner"].create({"name": "Partner Test"})

        # Producto sin depender de demo data
        cls.product = cls.env["product.product"].create(
            {
                "name": "Producto de prueba",
                "type": "consu",
                "list_price": 100.0,
            }
        )

        # Asegurar que existe un diario de caja
        cls.journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "cash")], limit=1
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Caja Test",
                    "code": "CST",
                    "type": "cash",
                    "company_id": cls.company.id,
                }
            )

        # Cargar un plan contable si no hay (tu lógica original era buena idea)
        if not cls.company.chart_template_id:
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                coa = cls.env["account.chart.template"].search([("visible", "=", True)], limit=1)
            if coa:
                coa.try_loading(company=cls.company, install_demo=False)

        # Factura cliente
        cls.invoice_out = cls.AccountMove.create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (0, 0, {"product_id": cls.product.id, "quantity": 1.0, "price_unit": 100.0})
                ],
            }
        )
        cls.invoice_out.action_post()

        # Factura proveedor
        cls.invoice_in = cls.AccountMove.create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.partner.id,
                "move_type": "in_invoice",
                "invoice_date": cls.env.context.get("date") or None,
                "invoice_line_ids": [
                    (0, 0, {"product_id": cls.product.id, "quantity": 1.0, "price_unit": 100.0})
                ],
            }
        )
        cls.invoice_in.action_post()

    def test_bank_statement(self):
        wizard_model = self.env["cash.pay.invoice"]

        with Form(wizard_model) as wiz_in:
            wiz_in.journal_id = self.journal
            wiz_in.invoice_type = "vendor"
            wiz_in.invoice_id = self.invoice_in
            self.assertEqual(-100, wiz_in.amount)

        wizard_model.browse(wiz_in.id).action_pay_invoice()

        with Form(wizard_model) as wiz_out:
            wiz_out.journal_id = self.journal
            wiz_out.invoice_type = "customer"
            wiz_out.invoice_id = self.invoice_out
            self.assertEqual(100, wiz_out.amount)

        wizard_model.browse(wiz_out.id).action_pay_invoice()

        self.assertEqual(self.invoice_out.amount_residual, 0.0)
        self.assertEqual(self.invoice_in.amount_residual, 0.0)
