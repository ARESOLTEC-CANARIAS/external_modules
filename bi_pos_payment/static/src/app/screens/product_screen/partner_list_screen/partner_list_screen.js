/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { RegisterPaymentPopupWidget } from "@bi_pos_payment/app/utils/register_payment_popup/register_payment_popup";

patch(PartnerList.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.dialog = useService("dialog");
    },

    addPayment(partner) {
        var confirmed = this.dialog.add(RegisterPaymentPopupWidget, { 'partner': partner });
        console.log("\n\n confirmed...", confirmed)
        this.props.close();
    }
});

