import { useState, onWillStart, onWillRender, onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

import { ProductConfiguratorPopup } from "@point_of_sale/app/store/product_configurator_popup/product_configurator_popup";
import { getProductQty } from "@wise_pos_stock/utils";

patch(ProductConfiguratorPopup.prototype, {
  getOpenOrderProductQty(productId) {
    let wise_qty = 0;
    this.pos.get_open_orders().forEach((order) => {
      order.get_orderlines().forEach((line) => {
        if (line.product_id.id === productId) {
          wise_qty += line.qty;
        }
      });
    });
    return wise_qty;
  },

  isProductOutOfStock() {
    const product = this.state.product;
    const wise_open_order_qty = this.getOpenOrderProductQty(product.id);
    const product_qty = getProductQty(this.pos.config.stock_type, product);
    return product_qty - wise_open_order_qty <= 0;
  },
});
