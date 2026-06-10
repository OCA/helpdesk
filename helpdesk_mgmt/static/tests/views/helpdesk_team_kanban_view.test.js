import {
    defineModels,
    mockService,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {animationFrame} from "@odoo/hoot-mock";
import {click} from "@odoo/hoot-dom";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class HelpdeskTicketTeam extends models.Model {
    _name = "helpdesk.ticket.team";

    _records = [{id: 1}, {id: 2}];

    fetch_agent_overview() {
        return {
            sample_mode: false,
            assigned_open: {
                any: {ticket_count: 4, mean_open_hours: 3.5},
                high: {ticket_count: 1, mean_open_hours: 2},
                urgent: {ticket_count: 0, mean_open_hours: 0},
            },
            assigned_closed: {today: 2, last_7_days: 5},
        };
    }

    _views = {
        "form,1": `
            <form>
                <group>
                    <field name="id"/>
                </group>
            </form>
        `,
        list: `
            <list>
                <field name="id" />
            </list>
        `,
    };
}

defineModels([HelpdeskTicketTeam]);
defineMailModels();

const overviewKanbanArch = `
    <kanban js_class="helpdesk_mgmt_overview_kanban">
        <templates>
            <t t-name="card">
                <field class="text-muted" name="id"/>
            </t>
        </templates>
    </kanban>`;

test("Helpdesk overview banner is rendered", async () => {
    await mountView({
        type: "kanban",
        resIds: [1],
        resModel: "helpdesk.ticket.team",
        arch: overviewKanbanArch,
    });
    expect(`.o_helpdesk_overview_strip`).toHaveCount(1);
    expect(`.o_overview_matrix`).toHaveCount(2);
    expect(`.o_helpdesk_overview_strip .fs-2`).toHaveCount(3);
    expect(`.o_helpdesk_overview_strip .fs-2:eq(0)`).toHaveText("4");
    expect(`.o_helpdesk_overview_strip .fs-2:eq(1)`).toHaveText("1");
    expect(`.o_helpdesk_overview_strip .fs-2:eq(2)`).toHaveText("0");
});

test("Helpdesk overview banner link triggers overview action", async () => {
    mockService("action", {
        async doActionButton(params) {
            expect.step("doActionButton");
            expect(params.resModel).toBe("helpdesk.ticket");
            expect(params.name).toBe("action_open_from_xmlid");
        },
    });
    await mountView({
        type: "kanban",
        resIds: [1],
        resModel: "helpdesk.ticket.team",
        arch: overviewKanbanArch,
    });
    await click(`.o_helpdesk_overview_strip a[data-hotkey="t"]`);
    await animationFrame();
    expect.verifySteps(["doActionButton"]);
});

test("Helpdesk overview sample mode blocks banner clicks", async () => {
    onRpc("helpdesk.ticket.team", "fetch_agent_overview", () => ({
        sample_mode: true,
        assigned_open: {
            any: {ticket_count: 7, mean_open_hours: 24},
            high: {ticket_count: 2, mean_open_hours: 8.5},
            urgent: {ticket_count: 1, mean_open_hours: 11},
        },
        assigned_closed: {today: 2, last_7_days: 11},
    }));
    mockService("action", {
        async doActionButton() {
            expect.step("doActionButton");
        },
    });
    await mountView({
        type: "kanban",
        resIds: [1],
        resModel: "helpdesk.ticket.team",
        arch: overviewKanbanArch,
    });
    expect(`.ribbon .text-bg-primary`).toHaveText("SAMPLE");
    await click(`.o_helpdesk_overview_strip a[data-hotkey="t"]`);
    await animationFrame();
    expect.verifySteps([]);
});
