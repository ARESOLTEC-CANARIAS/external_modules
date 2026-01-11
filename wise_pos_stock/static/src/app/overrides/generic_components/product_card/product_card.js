import { patch } from "@web/core/utils/patch";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

patch(ProductCard, {
  props: {
    ...ProductCard.props,
    wise_quantites: { Array, optional: true },
    is_display_stock: { String, optional: true },
    display_total_variant_stock: { String, optional: true },
  },
});
