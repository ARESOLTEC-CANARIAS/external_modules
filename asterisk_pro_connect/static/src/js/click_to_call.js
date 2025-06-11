/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ClickToCallWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.state = useState({
            isLoading: false,
            userConfig: null,
        });

        onMounted(async () => {
            await this.loadUserConfig();
        });
    }

    async loadUserConfig() {
        try {
            const result = await this.rpc("/asterisk/user_config");
            if (result.success) {
                this.state.userConfig = result.config;
            }
        } catch (error) {
            console.error("Error loading user config:", error);
        }
    }

    async makeCall(phoneNumber, partnerId = null, leadId = null) {
        if (!this.state.userConfig || !this.state.userConfig.click_to_call_enabled) {
            this.notification.add("Click-to-call is not enabled", { type: "warning" });
            return;
        }

        if (!phoneNumber) {
            this.notification.add("No phone number provided", { type: "warning" });
            return;
        }

        this.state.isLoading = true;

        try {
            const result = await this.rpc("/asterisk/click_to_call", {
                phone_number: phoneNumber,
                partner_id: partnerId,
                lead_id: leadId,
            });

            if (result.success) {
                this.notification.add(result.message, { type: "success" });
            } else {
                this.notification.add(result.error, { type: "danger" });
            }
        } catch (error) {
            this.notification.add("Error making call", { type: "danger" });
            console.error("Click-to-call error:", error);
        } finally {
            this.state.isLoading = false;
        }
    }
}

ClickToCallWidget.template = "asterisk_pro_connect.ClickToCallWidget";

// Register the widget
registry.category("fields").add("click_to_call", ClickToCallWidget);

// Phone field widget with click-to-call functionality
export class PhoneFieldWidget extends Component {
    setup() {
        this.clickToCall = new ClickToCallWidget();
    }

    get phoneNumber() {
        return this.props.value || "";
    }

    get partnerId() {
        return this.props.record.data.id || null;
    }

    get leadId() {
        return this.props.record.resModel === "crm.lead" ? this.props.record.data.id : null;
    }

    onCallClick() {
        this.clickToCall.makeCall(this.phoneNumber, this.partnerId, this.leadId);
    }
}

PhoneFieldWidget.template = "asterisk_pro_connect.PhoneFieldWidget";
PhoneFieldWidget.supportedTypes = ["char"];

registry.category("fields").add("phone_click_to_call", PhoneFieldWidget);

