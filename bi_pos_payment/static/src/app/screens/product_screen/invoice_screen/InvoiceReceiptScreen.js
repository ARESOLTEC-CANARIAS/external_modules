import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { InvoiceReceipt } from "@bi_pos_payment/app/screens/product_screen/invoice_screen/InvoiceReceipt"

export class InvoiceReceiptScreen extends ReceiptScreen {
    static template = "bi_pos_payment.InvoiceReceiptScreen";
    static components = { InvoiceReceipt }
    static props = ['invoice_name', 'invoice_customer', 'invoice_amount', 'invoice_note', 'invoice_number']

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
            InvoiceReceipt,
            {
                order: this.invoice_receipt_data,
            },
            { webPrintFallback: true }
        );
    }

    get invoice_receipt_data() {
        return {
            invoice_name: this['props']['invoice_name'],
            invoice_customer:this['props']['invoice_customer'],
            invoice_amount : this['props']['invoice_amount'],
            invoice_note : this['props']['invoice_note'],
            invoice_number: this['props']['invoice_number']
            
        };

    }
}

registry.category("pos_screens").add("InvoiceReceiptScreen", InvoiceReceiptScreen);