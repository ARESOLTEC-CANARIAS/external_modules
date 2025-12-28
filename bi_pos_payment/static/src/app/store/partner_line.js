/* @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";

patch(PosStore.prototype, {
    async processServerData(loadedData) {
        await super.processServerData(...arguments);
        this.invoices = this.data.models['account.move'].getAll();
        this.journals = this.data.models["account.journal"].getAll();
    }
});

patch(PartnerLine, {
    props: [
        ...PartnerLine.props,
        "onClickPayment",
    ],
});