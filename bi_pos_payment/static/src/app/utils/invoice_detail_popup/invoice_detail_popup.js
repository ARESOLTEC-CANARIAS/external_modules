/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { RegisterInvoicePaymentPopupWidget } from "@bi_pos_payment/app/utils/register_invoice_payment_popup/register_invoice_payment_popup";

export class PosInvoiceDetail extends Component {
	static template = "bi_pos_payment.PosInvoiceDetail";
	static components = { Dialog };

	setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService("orm");
		this.partner = this.partner;
		this.poscurrency = this.poscurrency || []
		this.dialog = useService("dialog");

	}
	static props = {

		order: Object,
		close: { type: Function },

	};
	async register_payment() {
		this.props.close({ confirmed: true });
		this.dialog.add(RegisterInvoicePaymentPopupWidget, { 'invoice': this.props.order });
	}
	async get_poscurrency() {
		let self = this;
		let load_currency = [];
		var fields = ['name', 'symbol', 'position', 'rounding', 'rate']
		await self.env.services.orm.call(
			'res.currency',
			'search_read',
			[[['active', '=', 'true']], fields],
		).then(function (output) {
			load_currency = output
		});
		this.poscurrency.push(load_currency)
	}
}