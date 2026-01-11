export function getProductQty(stockType, product) {
  const qty =
    stockType == "on_hand" ? product.qty_available : product.virtual_available;
  return qty;
}

export function getOpenOrderProductQty(productId, orders) {
  let wise_qty = 0;
  orders.forEach((order) => {
    order.get_orderlines().forEach((line) => {
      if (line.product_id.id === productId) {
        wise_qty += line.qty;
      }
    });
  });
  return wise_qty;
}
