import {Component, onWillStart, proxy, usePlugin} from "@odoo/owl";
import {UIPlugin} from "@web/core/ui/ui_plugin";
import {useBus, useService} from "@web/core/utils/hooks";
import {SIZES} from "@web/core/ui/ui_utils";
import {ViewButton} from "@web/views/view_button/view_button";
import {ActionPlugin} from "@web/webclient/actions/action_plugin";

export class HelpdeskDashboard extends Component {
    static template = "helpdesk_mgmt.HelpdeskDashboard";
    static components = {ViewButton};
    setup() {
        this.orm = useService("orm");
        this.action = usePlugin(ActionPlugin);
        this.uiService = usePlugin(UIPlugin);
        useBus(this.uiService.bus, "resize", this.updateGridTemplateColumns.bind(this));
        this.state = proxy({
            gridTemplateColumns: this._getGridTemplateColumns(),
        });
        onWillStart(async () => {
            this.helpdeskData = await this.orm.call(
                "helpdesk.ticket.team",
                "retrieve_dashboard"
            );
        });
    }
    clickParams(section) {
        if (section.action) {
            return {name: section.action, type: "action"};
        }
        return {};
    }

    _getGridTemplateColumns() {
        switch (this.uiService.size()) {
            case SIZES.XS:
                return 2;
            case SIZES.SM:
                return 3;
            case SIZES.XXL:
                return 6;
            default:
                return 4;
        }
    }

    updateGridTemplateColumns() {
        this.state.gridTemplateColumns = this._getGridTemplateColumns();
    }
}
