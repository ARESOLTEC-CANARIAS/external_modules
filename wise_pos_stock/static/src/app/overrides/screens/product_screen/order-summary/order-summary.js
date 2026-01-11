import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { getProductQty, getOpenOrderProductQty } from "@wise_pos_stock/utils";

patch(OrderSummary.prototype, {
  /**
   * TODO
   *  The updateSelectedOrderline method is invoked for every action.
   *  If the _setValue function does not fully meet the module's requirements,
   *  we will implement the necessary logic within this function.
   */
  //async updateSelectedOrderline() {},
  _setValue(val) {
    const { numpadMode } = this.pos;
    const selectedLine = this.currentOrder.get_selected_orderline();
    if (!selectedLine) {
      return;
    }
    const openOrders = this.pos.get_open_orders();
    const openOrderProductQty = getOpenOrderProductQty(
      selectedLine.product_id.id,
      openOrders,
    );
    const productQty = getProductQty(
      this.pos.config.stock_type,
      selectedLine.product_id,
    );
    if (
      selectedLine &&
      numpadMode === "quantity" &&
      val !== "remove" &&
      selectedLine.product_id.is_storable &&
      productQty - (openOrderProductQty - selectedLine.qty) < val
    ) {
      this.env.services.dialog.add(AlertDialog, {
        title: _t("Insufficient Stock"),
        body: _t(
          "The quantity entered exceeds the available stock. Please enter a quantity less than or equal to the available stock.",
        ),
      });
      this.numberBuffer.reset();
      return;
    } else {
      super._setValue(val);
    }
  },
});
