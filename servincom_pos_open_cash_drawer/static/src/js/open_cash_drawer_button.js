odoo.define("servincom_pos_open_cash_drawer.OpenCashDrawerButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");

    class OpenCashDrawerButton extends PosComponent {
        async onClick() {
            if (this.env.proxy && this.env.proxy.printer) {
                this.env.proxy.printer.open_cashbox();
                return;
            }

            await this.showPopup("ErrorPopup", {
                title: this.env._t("Cash drawer unavailable"),
                body: this.env._t(
                    "Connect and configure a cash drawer before using this button."
                ),
            });
        }
    }

    OpenCashDrawerButton.template =
        "servincom_pos_open_cash_drawer.OpenCashDrawerButton";

    ProductScreen.addControlButton({
        component: OpenCashDrawerButton,
        condition: function () {
            return this.env.pos.config.iface_cashdrawer;
        },
    });

    Registries.Component.add(OpenCashDrawerButton);

    return OpenCashDrawerButton;
});
