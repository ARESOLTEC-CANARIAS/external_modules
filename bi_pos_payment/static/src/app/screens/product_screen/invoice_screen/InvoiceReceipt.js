/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";

export class InvoiceReceipt extends Component {
    static template = "bi_pos_payment.InvoiceReceipt";
    static props = ['order']
    
    setup() {
        this.pos = usePos();
    }
   
}
