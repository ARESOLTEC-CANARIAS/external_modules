import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, {
    _onCreateTimesheets() {
        console.log(this);
        this.actionService.doAction(
            'andamios_extend.create_account_analytic_line_wizard_action', 
            {}
        );
    },
});