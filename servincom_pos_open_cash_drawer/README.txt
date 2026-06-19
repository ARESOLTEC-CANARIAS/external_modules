SERVINCOM POS Open Cash Drawer

This module adds an Open Cash Drawer button to the Point of Sale product
screen.

The button is shown when the standard cash drawer option is enabled in the POS
configuration.

Use it for shops that need to open the configured cash drawer without
validating a payment.

Technical notes:

- Requires Point of Sale.
- Uses the standard Odoo POS proxy printer open_cashbox method.
- The cash drawer must be configured and available through the POS hardware
  proxy or IoT setup.
