/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { PosInvoiceDetail } from "@bi_pos_payment/app/utils/invoice_detail_popup/invoice_detail_popup"
//import { InvoiceScreen } from "@bi_pos_payment/app/screens/product_screen/invoice_screen/invoice_screen";


export class InvoiceLine extends Component {
    static template = "bi_pos_payment.InvoiceLine";

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }
    static props = {
        order: Object,
        onClickPosOrder: Function,

    };

    showDetails(order) {
        
        let self = this;
        self.dialog.add(PosInvoiceDetail, {
            'order': order,
        });
//        Parent.prototype.back()
//        InvoiceScreen.prototype.back()


    }
}
