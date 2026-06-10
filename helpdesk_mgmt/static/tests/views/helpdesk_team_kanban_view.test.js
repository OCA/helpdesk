import {
    defineActions,
    defineModels,
    models,
    mountView,
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

defineActions([
    {
        id: 1,
        xml_id: "helpdesk_mgmt.overview_agent_open_tickets_window",
        name: "My Tickets",
        res_model: "helpdesk.ticket",
        view_mode: "kanban,list,form",
        views: [[false, "kanban"]],
    },
]);

defineModels([HelpdeskTicketTeam]);
defineMailModels();

test("Helpdesk overview banner is rendered", async () => {
    await mountView({
        type: "kanban",
        resIds: [1],
        resModel: "helpdesk.ticket.team",
        arch: `
            <kanban js_class="helpdesk_mgmt_overview_kanban">
                <templates>
                    <t t-name="card">
                        <field class="text-muted" name="id"/>
                    </t>
                </templates>
            </kanban>`,
    });
    expect(`.o_helpdesk_overview_strip`).toHaveCount(1);
    expect(`.o_overview_matrix`).toHaveCount(2);
    expect(`.o_helpdesk_overview_strip .fs-2`).toHaveCount(3);
    expect(`.o_helpdesk_overview_strip .fs-2:eq(0)`).toHaveText("4");
    expect(`.o_helpdesk_overview_strip .fs-2:eq(1)`).toHaveText("1");
    expect(`.o_helpdesk_overview_strip .fs-2:eq(2)`).toHaveText("0");
    await click(
        `.o_helpdesk_overview_strip a[name='helpdesk_mgmt.overview_agent_open_tickets_window']`
    );
    await animationFrame();
});
