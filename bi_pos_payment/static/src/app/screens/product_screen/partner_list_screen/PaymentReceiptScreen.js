import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { PaymentReceipt } from "@bi_pos_payment/app/screens/product_screen/partner_list_screen/PaymentReceipt"

export class PaymentReceiptScreen extends ReceiptScreen {
    static template = "bi_pos_payment.PaymentReceiptScreen";
    static components = { PaymentReceipt }
    static props = ['payment_name', 'payment_customer', 'payment_amount', 'payment_note']

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.printer = useService("printer");
    }

    back() {
        this.pos.showScreen('ProductScreen');
    }
	
	async printReceipt() {
        const isPrinted = await this.printer.print(
            PaymentReceipt,
            {
                order: this.payment_receipt_data,
            },
            { webPrintFallback: true }
        );
    }

    get payment_receipt_data() {
        return {
            payment_name: this['props']['payment_name'],
            payment_customer:this['props']['payment_customer'],
            payment_amount : this['props']['payment_amount'],
            payment_note : this['props']['payment_note'],
            
        };

    }
}

registry.category("pos_screens").add("PaymentReceiptScreen", PaymentReceiptScreen);