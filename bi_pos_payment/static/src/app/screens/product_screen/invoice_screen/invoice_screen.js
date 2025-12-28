/** @odoo-module */
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState, Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

import { useService } from "@web/core/utils/hooks";
import { InvoiceLine } from "@bi_pos_payment/app/screens/product_screen/invoice_screen/invoice_line/invoice_line";

export class InvoiceScreen extends Component {
    static components = { InvoiceLine };
    static template = "bi_pos_payment.InvoiceScreen";


    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.env.services.pos.get_so_line_by_id = {};
        this.state = useState({ all_invoice_data: [] || false, all_invoice_data_line: [] || false, selectedPosOrder: this.props.partner });
    }

    back() {
        this.pos.showScreen("ProductScreen");
    }
    clickPosOrder(invoices) {
        let order = invoices;
        if (this.state.selectedPosOrder === order) {
            this.state.selectedPosOrder = null;
        } else {
            this.state.selectedPosOrder = order;
        }
        this.render();
    }
    async get_all_invoice_data() {
        let self = this;

        var fields = ['name', 'partner_id', 'amount_total', 'amount_residual', 'currency_id', 'state', 'payment_state', 'move_type']
        let load_invoice = [];
        let load_invoice_line = [];
        let inv_ids = [];
        try {
            await self.env.services.orm.call(
                'account.move',
                'search_read',
                [[['state', '=', 'posted'], ['move_type', '=', 'out_invoice'], ['payment_state', '!=', 'paid']], fields],
            ).then(function (output) {
                load_invoice = output;
                self.env.services.pos.get_so_by_id = {};
                load_invoice.forEach(function (inv) {
                    inv_ids.push(inv.id)
                    self.env.services.pos.get_so_by_id[inv.id] = inv;
                });
                let fields_domain = [['move_id', 'in', inv_ids]];
                let fields = ['name', 'move_id']
                self.env.services.orm.call(
                    'account.move.line',
                    'search_read',
                    [fields_domain],

                ).then(function (output1) {
                    load_invoice_line = output1;
                    self.orders = load_invoice;
                    self.orderlines = output1;
                    self.env.services.pos.get_so_line_by_id = {};
                    output1.forEach(function (ol) {
                        self.env.services.pos.get_so_line_by_id[ol.id] = ol;
                    });
                });
            });
            if (this.state.all_invoice_data.length == 0) {
                this.state.all_invoice_data.push(load_invoice)
            }
        }
        catch (error) {
            if (error.message.code < 0) {

                return this.dialog.add(AlertDialog, {
                    title: _t('Offline'),
                    body: _t('Unable to load orders.'),
                });
            } else {
                throw error;
            }
        }

    }
}
registry.category("pos_screens").add("InvoiceScreen", InvoiceScreen);

