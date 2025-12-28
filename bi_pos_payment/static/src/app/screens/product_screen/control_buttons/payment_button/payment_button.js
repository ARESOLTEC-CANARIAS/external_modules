/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";


patch(ControlButtons.prototype, {

    setup() {
        super.setup();
    },
    async onClickPaymentCustom() {
        var self = this;
        var currentOrder = self.pos.get_order()
        const currentPartner = currentOrder.get_partner();
        console.log("==currentPartner0",currentPartner)
        if (currentPartner){
            this.dialog.add(PartnerList, {
                partner: currentPartner,
                getPayload: (newPartner) => currentOrder.set_partner(newPartner),
            });
        }else{
            this.dialog.add(PartnerList, {
                getPayload: (newPartner) => currentOrder.set_partner(false),
            });
        }
    },
});
