/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class RegisterPaymentPopupWidget extends Component {
	static template = "bi_pos_payment.RegisterPaymentPopupWidget";
	static components = { Dialog };

	setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService("orm");
	}
	static props = {
		partner: Object,
		close: { type: Function, optional: true },
	}
	register_payment() {
		var self = this;
		let partner = this.props.partner;
		var payment_type = document.getElementById("payment_type")?.value;
		var entered_amount = document.getElementById("entered_amount")?.value;
		var entered_note = document.getElementById("entered_note")?.value
		var amount = parseFloat(entered_amount);

		if (!entered_amount || isNaN(amount) || amount <= 0) {
			alert('Please enter a valid amount greater than zero!');
		} else {
			self.orm.call('pos.create.customer.payment', 
				'create_customer_payment',
				[partner ? partner.id : 0, partner ? partner.id : 0, payment_type, entered_amount, entered_note],
			).then(function (output) {
				alert('Payment has been Registered for this Customer !!!!');
				let payment_name=output[0]
					let payment_customer=output[1]
					let payment_amount=output[2]
					let payment_note=output[3]
					self.props.close({ confirmed: true});
					self.pos.showScreen('PaymentReceiptScreen',{
						payment_name:payment_name,
						payment_customer:payment_customer,
						payment_amount:payment_amount,
						payment_note:payment_note,
					});
			});
		}
	}
}