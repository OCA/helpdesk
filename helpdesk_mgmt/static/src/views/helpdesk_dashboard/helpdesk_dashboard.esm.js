import {Component, onWillStart, useState} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {SIZES} from "@web/core/ui/ui_service";
import {ViewButton} from "@web/views/view_button/view_button";

export class HelpdeskDashboard extends Component {
    static template = "helpdesk_mgmt.HelpdeskDashboard";
    static props = {};
    static components = {ViewButton};
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.uiService = useService("ui");
        useBus(this.uiService.bus, "resize", this.updateGridTemplateColumns);
        this.state = useState({
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
        switch (this.uiService.size) {
            case SIZES.XS:
                return 2;
            case SIZES.VSM:
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
