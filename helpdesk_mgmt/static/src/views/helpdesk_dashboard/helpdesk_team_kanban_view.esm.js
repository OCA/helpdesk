/** @odoo-module **/

import {HelpdeskTeamDashboard} from "./helpdesk_team_dashboard.esm";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export class HelpdeskMgmtOverviewKanbanController extends KanbanController {
    static template = "helpdesk_mgmt.HelpdeskOverviewKanbanView";
    static components = {
        ...KanbanController.components,
        HelpdeskTeamDashboard,
    };
}

export const helpdeskMgmtOverviewKanbanView = {
    ...kanbanView,
    Controller: HelpdeskMgmtOverviewKanbanController,
    searchMenuTypes: ["filter", "groupBy", "favorite"],
};

registry
    .category("views")
    .add("helpdesk_mgmt_overview_kanban", helpdeskMgmtOverviewKanbanView);
