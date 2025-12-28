/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { InvoiceScreen } from "@bi_pos_payment/app/screens/product_screen/invoice_screen/invoice_screen";


patch(ControlButtons.prototype, {

    setup() {
        super.setup();
    },

    async onClickInvoiceCustom() {
        var self = this;
        await this.pos.showScreen('InvoiceScreen', {})
    },
});
