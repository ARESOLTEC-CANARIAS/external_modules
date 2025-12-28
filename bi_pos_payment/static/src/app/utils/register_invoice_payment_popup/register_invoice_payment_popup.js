/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";


export class RegisterInvoicePaymentPopupWidget extends Component {
    static template = "bi_pos_payment.RegisterInvoicePaymentPopupWidget";
    static components = { Dialog };
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
    }

    static props = {
        invoice: Object,
        close: { type: Function, optional: true },
    }

    register_payment() {
        var self = this;
        var invoice = this.props.invoice;
        var partner = invoice.partner_id[0];
        var payment_type = document.getElementById("payment_type1")?.value;
        var entered_amount = document.getElementById("entered_amount1")?.value;
        var entered_note = document.getElementById("entered_note1")?.value
        var amount = parseFloat(entered_amount);
        let rpc_result = false;

        if (!entered_amount || isNaN(amount) || amount <= 0) {
            alert('Please enter a valid amount greater than zero!');
        } else {
            if (invoice['amount_residual'] >= entered_amount) {
                rpc_result = self.orm.call('pos.create.customer.payment',
                    'create_customer_payment_inv',
                    [partner ? partner : 0, partner ? partner : 0, payment_type, entered_amount, invoice, entered_note],
                ).then(function (output) {
                    alert('Payment has been Registered for this Invoice !!!!');
                    let invoice_name=output[0]
                    let invoice_customer=output[1]
                    let invoice_amount=output[2]
                    let invoice_note=output[3]
                    self.props.close({ confirmed: false });
                    self.pos.showScreen('InvoiceReceiptScreen',{
                        invoice_name:invoice_name,
                        invoice_customer:invoice_customer,
                        invoice_amount:invoice_amount,
                        invoice_note:invoice_note,
                        invoice_number: invoice.name,
                    });
                    self.pos.dialog.closeAll()
                });

            }
            else {
                this.dialog.add(AlertDialog, {
                    'title': _t('Amount Error'),
                    'body': _t('Entered amount is larger then due amount. please enter valid amount'),
                });
            }
        }
    }
}