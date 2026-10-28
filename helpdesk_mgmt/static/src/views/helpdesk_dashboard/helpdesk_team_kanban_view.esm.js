import {HelpdeskDashboard} from "./helpdesk_dashboard.esm";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export class HelpdeskKanbanViewRenderer extends KanbanRenderer {
    static template = "helpdesk_mgmt.HelpdeskKanbanView";
    static components = Object.assign({}, KanbanRenderer.components, {
        HelpdeskDashboard,
    });
}

export const HelpdeskKanbanView = {
    ...kanbanView,
    Renderer: HelpdeskKanbanViewRenderer,
};

registry.category("views").add("helpdesk_kanban", HelpdeskKanbanView);
