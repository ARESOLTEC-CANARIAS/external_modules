import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { StockList } from "@wise_pos_stock/app/screens/stock_list/stock_list";
patch(Navbar.prototype, {
  async onStockListClick() {
    this.dialog.add(StockList);
  },
});
