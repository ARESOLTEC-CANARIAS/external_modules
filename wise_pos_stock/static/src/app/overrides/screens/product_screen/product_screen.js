import { useState, onWillStart, onWillRender, onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import {
  ConnectionLostError,
  ConnectionAbortedError,
} from "@web/core/network/rpc";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { getProductQty, getOpenOrderProductQty } from "@wise_pos_stock/utils";

patch(ProductScreen.prototype, {
  setup() {
    super.setup(...arguments);
    this.state = useState({
      previousSearchWord: "",
      currentOffset: 0,
      quantityByProductTmplId: {},
      wiseQuantitesByProductTmpId: this.getWiseQuantitesByProductTmpId(),
    });

    //** TODO: Check onWillStart and onWillRender both required */
    onWillStart(async () => {
      this.state.wiseQuantitesByProductTmpId =
        this.getWiseQuantitesByProductTmpId();
    });

    onMounted(() => {
      if (this.pos.config.update_stock_quantities === "real") {
        const refreshRate = this.pos.config.stock_quantities_refresh_rate;
        const refreshRateMS = refreshRate && refreshRate * 60000;
        this._runUpdateProductQtyTimer(refreshRateMS);
        this.loadLatestProductQtyFromDB();
      }
    });
  },
  _runUpdateProductQtyTimer(time = 180000) {
    this.updateProductQtyTimer = setInterval(() => {
      this.loadLatestProductQtyFromDB();
    }, time);
  },

  getClass(product) {
    let className = this.pos.productViewMode;
    // Only apply stock restriction for stockable products
    if (
      this.pos.config.is_restrict_out_of_stock_products &&
      product.is_storable
    ) {
      if (product.isConfigurable()) {
        const isAllQtyZero = product.wise_quantites.every(
          (item) => item.qty === 0,
        );
        if (isAllQtyZero) {
          className += " disabled";
        }
      } else {
        const openOrders = this.pos.get_open_orders();
        let qty = getProductQty(this.pos.config.stock_type, product);
        qty = qty - getOpenOrderProductQty(product.id, openOrders);
        className += qty <= 0 ? " disabled" : "";
      }
    }

    return className;
  },

  getWiseQuantitesByProductTmpId() {
    const products = this.productsToDisplay;
    return products.reduce((qtyByProductTmpId, product) => {
      qtyByProductTmpId[product.raw.product_tmpl_id] =
        this.getWiseProductQuantites(product);
      return qtyByProductTmpId;
    }, {});
  },

  getWiseProductQuantites(product) {
    const lowStockThreshold = this.pos.config.low_stock_threshold;
    const lowStockColor = `o_colorlist_item_color_${this.pos.config.low_stock_color}`;
    const inStockColor = `o_colorlist_item_color_${this.pos.config.in_stock_color}`;
    const openOrders = this.pos.get_open_orders();
    if (product.isConfigurable()) {
      const variants = this.pos.models["product.product"].filter(
        (p) => p.raw.product_tmpl_id === product.raw.product_tmpl_id,
      );
      const quantites = variants.map((variant) => {
        let wise_qty = getProductQty(this.pos.config.stock_type, variant);
        wise_qty = wise_qty - getOpenOrderProductQty(variant.id, openOrders);
        return {
          id: variant.id,
          qty: wise_qty,
          class: wise_qty <= lowStockThreshold ? lowStockColor : inStockColor,
        };
      });
      return quantites;
    } else {
      let wise_qty = getProductQty(this.pos.config.stock_type, product);
      wise_qty = wise_qty - getOpenOrderProductQty(product.id, openOrders);
      return [
        {
          id: product.id,
          qty: wise_qty,
          class: wise_qty <= lowStockThreshold ? lowStockColor : inStockColor,
        },
      ];
    }
  },
  getWiseTotalVariantStock(product) {
    const lowStockThreshold = this.pos.config.low_stock_threshold;
    const lowStockColor = `o_colorlist_item_color_${this.pos.config.low_stock_color}`;
    const inStockColor = `o_colorlist_item_color_${this.pos.config.in_stock_color}`;
    const openOrders = this.pos.get_open_orders();

    let total_qty = 0;

    if (product.isConfigurable()) {
      const variants = this.pos.models["product.product"].filter(
        (p) => p.raw.product_tmpl_id === product.raw.product_tmpl_id,
      );
      total_qty = variants.reduce((sum, variant) => {
        let wise_qty = getProductQty(this.pos.config.stock_type, variant);
        wise_qty -= getOpenOrderProductQty(variant.id, openOrders);
        return sum + wise_qty;
      }, 0);
    } else {
      let wise_qty = getProductQty(this.pos.config.stock_type, product);
      wise_qty -= getOpenOrderProductQty(product.id, openOrders);
      total_qty = wise_qty;
    }

    const stock_class =
      total_qty <= lowStockThreshold ? lowStockColor : inStockColor;

    return {
      qty: total_qty,
      class: stock_class,
    };
  },

  get productsToDisplay() {
    const products = super.productsToDisplay;
    const productsWithAttributes = products.map((product) => {
      product.wise_quantites = this.getWiseProductQuantites(product);
      product.total_variant_stock = this.getWiseTotalVariantStock(product);
      return product;
    });
    return productsWithAttributes;
  },

  async loadLatestProductQtyFromDB() {
    try {
      let kwargs = {};

      const product_product_record = this.pos.data.records["product.product"];
      const productIds = [...product_product_record.keys()];
      if (this.pos.config.stock_warehouse === "current") {
        kwargs.context = {
          location: this.pos.config.picking_type_location_id_num,
        };
      }
      const products = await this.pos.data.searchRead(
        "product.product",
        [["id", "in", productIds]],
        ["qty_available", "virtual_available"],
        kwargs,
      );
      if (products && products.length > 0) {
        products.forEach((product) => {
          const product_record = product_product_record.get(product.id);
          if (product_record) {
            Object.assign(product_record, product);
          }
        });
      }
    } catch (error) {
      if (
        error instanceof ConnectionLostError ||
        error instanceof ConnectionAbortedError
      ) {
        this.env.services.dialog.add(AlertDialog, {
          title: _t("Failure to load product"),
          body: _t(
            "Connection to the server has been lost. Please check your internet connection.",
          ),
        });
        return false;
      } else {
        throw error;
      }
    }
  },
  async wise_pay() {
    const currentOrder = this.currentOrder || this.pos.selectedOrder;
    const dialog = this.dialog || this.pos.dialog;
    if (
      currentOrder.lines.length > 0 &&
      this.pos.config.is_restrict_out_of_stock_products
    ) {
      const outOfStockProducts = [];
      currentOrder.lines.forEach((line) => {
        let qty = getProductQty(this.pos.config.stock_type, line.product_id);
        if (qty < line.qty && line.product_id.is_storable) {
          outOfStockProducts.push(line.product_id.display_name);
        }
      });
      if (outOfStockProducts && outOfStockProducts.length > 0) {
        dialog.add(AlertDialog, {
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
    this.pos.pay();
  },
});
