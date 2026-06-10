/** @odoo-module **/

import {user} from "@web/core/user";
import {evaluateExpr} from "@web/core/py_js/py";
import {formatFloatTime} from "@web/views/fields/formatters";
import {useService} from "@web/core/utils/hooks";
import {Component, onWillStart, useState} from "@odoo/owl";
import {overviewApiToBannerState} from "./overview_payload.esm";

const OVERVIEW_ACTION_PREFIX = "helpdesk_mgmt.";

export class HelpdeskTeamDashboard extends Component {
    static template = "helpdesk_mgmt.HelpdeskTeamDashboard";
    static props = {};

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({dashboardValues: null});
        onWillStart(() => this._loadMetrics());
    }

    get showDemo() {
        return Boolean(this.state.dashboardValues?.show_demo);
    }

    get demoClass() {
        return this.showDemo ? "o_demo o_disabled o_cursor_default" : "";
    }

    async _loadMetrics() {
        const payload = await this.orm.call(
            "helpdesk.ticket.team",
            "fetch_agent_overview",
            [],
            {context: user.context}
        );
        this.state.dashboardValues = overviewApiToBannerState(payload);
    }

    /**
     * @param {MouseEvent} ev
     */
    async onActionClicked(ev, newWindow) {
        if (this.showDemo) {
            return;
        }
        const link = ev.currentTarget;
        const xmlId = link.getAttribute("name");
        if (!xmlId?.startsWith(OVERVIEW_ACTION_PREFIX)) {
            return this.action.doAction(xmlId, {newWindow});
        }
        const title = link.dataset.actionTitle || link.getAttribute("title");
        const searchViewRef = link.getAttribute("search_view_ref");
        let buttonContext = {};
        const contextAttr = link.getAttribute("context");
        if (contextAttr) {
            buttonContext = evaluateExpr(contextAttr, {});
        }
        return this.action.doActionButton(
            {
                resModel: "helpdesk.ticket",
                name: "action_open_from_xmlid",
                args: JSON.stringify([xmlId, title, searchViewRef]),
                context: {},
                buttonContext,
                type: "object",
            },
            {newWindow}
        );
    }

    formatTime(value, options = {}) {
        return formatFloatTime(value, options);
    }
}
