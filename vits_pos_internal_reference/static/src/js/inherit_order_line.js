/* @odoo-module */
/**
 * ###########################################################################
 * Author      : Varanval IT Solutions
 * Copyright   : (c) 2025 Varanval IT Solutions. All Rights Reserved.
 *
 * This JavaScript file is part of a paid Odoo module developed by Varanval IT Solutions.
 *
 * This module is licensed only for use by the customer who has purchased it,
 * and only for the number of users specified at the time of purchase.
 *
 * For licensing inquiries, contact: markvaranval@gmail.com
 * ###########################################################################
 */
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";


let allow_on_receipt  = false;

rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
    model: 'ir.config_parameter',
    method: 'get_param',
    args: ['res.config.settings.allow_default_code_receipt'],
    kwargs: {},
}).then((result) => {
    allow_on_receipt  = result === 'True';
});


patch(PosOrderline.prototype, {

    get_full_product_name() {
        var result = super.get_full_product_name()
        if (allow_on_receipt && this.product_id.default_code) {
            result = result + " " + "[" + this.product_id.default_code + "]"
        }
        return result
    }

});
