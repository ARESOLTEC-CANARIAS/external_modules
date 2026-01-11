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
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";

let allowDefaultCode  = false;

rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
    model: 'ir.config_parameter',
    method: 'get_param',
    args: ['res.config.settings.allow_default_code_pos_screen'],
    kwargs: {},
}).then((result) => {
    allowDefaultCode  = result === 'True';
});

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
    },

    getProductName(product) {
        var result = super.getProductName(...arguments);
        if (allowDefaultCode  && product.default_code) {
            result = result + " " + "[" + product.default_code + "]"
        }
        return result
    }

});
