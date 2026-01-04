# Copyright (C) 2017-2021 Creu Blanca
# Copyright (C) 2024 Tecnativa <https://tecnativa.com>
# Copyright (C) 2026 Servincom Soluciones
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _action_show_pay_invoice_wizard(self, move_type):
        self.ensure_one()

        # IMPORTANTE: usar la acción del módulo pos_session_pay_invoice
        # para asegurar que se abre la vista heredada con pos_payment_method_id
        action = self.env.ref(
            "pos_session_pay_invoice.action_pos_invoice_in_control"
        ).read()[0]

        # Elegir método de pago por defecto
        payment_methods = self.payment_method_ids.filtered(
            lambda pm: pm.journal_id and pm.journal_id.type in ("cash", "bank")
        )
        if move_type == "in_invoice":
            payment_methods = payment_methods.filtered(
                lambda pm: pm.journal_id.type == "cash"
            )

        default_pm = payment_methods[:1]

        ctx = dict(self.env.context or {})
        ctx.update(
            {
                "default_pos_session_id": self.id,
                "pos_pay_invoice_domain": move_type,
                # Esto alimenta el default_get del wizard heredado
                "pos_pay_invoice_type": "vendor"
                if move_type in ("in_invoice", "out_refund")
                else "customer",
            }
        )

        if default_pm:
            ctx.update(
                {
                    "default_pos_payment_method_id": default_pm.id,
                    "default_journal_id": default_pm.journal_id.id,
                }
            )

        action["context"] = ctx
        return action

    def button_show_wizard_pay_out_invoice(self):
        self.ensure_one()
        return self._action_show_pay_invoice_wizard("out_invoice")

    def button_show_wizard_pay_out_refund(self):
        self.ensure_one()
        return self._action_show_pay_invoice_wizard("out_refund")

    def button_show_wizard_pay_in_invoice(self):
        self.ensure_one()
        return self._action_show_pay_invoice_wizard("in_invoice")
