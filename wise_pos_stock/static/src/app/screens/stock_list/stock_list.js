import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState } from "@odoo/owl";

export class StockList extends Component {
  static components = { Dialog };
  static template = "wise_pos_stock.StockList";

  // static props = {
  //   close: { type: Function },
  // };

  setup() {
    this.pos = usePos();
    this.ui = useState(useService("ui"));
    this.dialog = useService("dialog");
  }

  getProductQty(stockType, product) {
    const qty =
      stockType == "on_hand"
        ? product.qty_available
        : product.virtual_available;
    return qty;
  }
  get products() {
    console.log("----->>>", this.pos.config.low_stock_threshold);
    const lowStockProduct = [];
    const lowStockThreshold = this.pos.config.low_stock_threshold;

    const products = this.pos.models["product.product"].getAll();

    for (let key in products) {
      const qty = this.getProductQty(this.pos.config.stock_type, products[key]);
      console.log(
        "---->>>",
        products[key],
        qty,
        lowStockThreshold,
        qty <= lowStockThreshold,
      );
      if (qty <= lowStockThreshold) {
        lowStockProduct.push(products[key]);
      }
    }
    return lowStockProduct;
  }
}
