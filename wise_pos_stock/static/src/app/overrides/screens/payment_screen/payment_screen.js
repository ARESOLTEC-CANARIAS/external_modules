import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { getProductQty, getOpenOrderProductQty } from "@wise_pos_stock/utils";

patch(PaymentScreen.prototype, {
  async validateOrder() {
    if (
      this.currentOrder.lines.length > 0 &&
      this.pos.config.is_restrict_out_of_stock_products
    ) {
      const outOfStockProducts = [];
      this.currentOrder.lines.forEach((line) => {
        let qty = getProductQty(this.pos.config.stock_type, line.product_id);
        if (qty < line.qty && line.product_id.is_storable) {
          outOfStockProducts.push(line.product_id.display_name);
        }
      });
      if (outOfStockProducts && outOfStockProducts.length > 0) {
        this.dialog.add(AlertDialog, {
          title: _t("Insufficient Stock"),
          body: _t(
            `The quantity entered exceeds the available stock. Please enter a quantity less than or equal to the available stock. [${outOfStockProducts.join(
              ",",
            )}]`,
          ),
        });
        return;
      }
    }

    return super.validateOrder(...arguments);
  },
});

//**
// TODO: _finalizeValidation not implemented from version 17
//
//  */
