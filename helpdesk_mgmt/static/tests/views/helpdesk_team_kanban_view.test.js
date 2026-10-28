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
    /*
        We cannot use json, because odoo is passing JSON as strings on the test
        but it is an object in real life :(
    */

    _records = [
        {
            id: 1,
        },
        {
            id: 2,
        },
        {
            id: 3,
        },
    ];

    retrieve_dashboard() {
        return [
            {
                name: "Open Tickets without team",
                value: 0,
                sequence: 1,
                icon: "error",
                show: false,
                action: "action_1",
            },
            {
                name: "Open Tickets without team",
                value: 11,
                sequence: 1,
                icon: "support_agent",
                show: true,
                action: "action_2",
            },
            {
                name: "Open Tickets 2 without team",
                value: 12,
                sequence: 1,
                icon: "settings",
                show: true,
                action: "action_3",
            },
        ];
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
        xml_id: "action_1",
        name: "Action 1",
        res_model: "helpdesk.ticket.team",
        res_id: 1,
        res_ids: [1],
        view_mode: "form",
        target: "new",
        views: [[1, "form"]],
    },
    {
        id: 2,
        xml_id: "action_2",
        name: "Action 2",
        res_model: "helpdesk.ticket.team",
        res_id: 2,
        res_ids: [2],
        view_mode: "form",
        target: "new",
        views: [[1, "form"]],
    },
    {
        id: 3,
        xml_id: "action_3",
        name: "Action 3",
        res_model: "helpdesk.ticket.team",
        res_id: 3,
        res_ids: [3],
        view_mode: "form",
        target: "new",
        views: [[1, "form"]],
    },
]);

defineModels([HelpdeskTicketTeam]);
defineMailModels();

test("Check Automation Graph Widget", async () => {
    await mountView({
        type: "kanban",
        resIds: [1],
        resModel: "helpdesk.ticket.team",
        arch: `

            <kanban js_class="helpdesk_kanban">
                <templates>
                    <t t-name="card">
                        <field class="text-muted" name="id"/>
                    </t>
                </templates>
            </kanban>`,
    });
    expect(`.o_helpdesk_team_dashboard`).toHaveCount(1);
    expect(`.o_helpdesk_team_dashboard button`).toHaveCount(2);
    expect(`.o_helpdesk_team_dashboard button [data-icon="error"]`).toHaveCount(0);
    expect(`.o_helpdesk_team_dashboard button [data-icon="support_agent"]`).toHaveCount(
        1
    );
    expect(`.o_helpdesk_team_dashboard button [data-icon="settings"]`).toHaveCount(1);
    await click(`.o_helpdesk_team_dashboard button [data-icon="support_agent"]`);
    await animationFrame();
    expect(`.o-main-components-container .o_dialog .o_form_view`).toHaveCount(1);
    expect(
        `.o-main-components-container .o_dialog .o_form_view [name='id'] span`
    ).toHaveCount(1);
    expect(
        `.o-main-components-container .o_dialog .o_form_view [name='id'] span`
    ).toHaveText("2");
    await click(`.o-main-components-container .o_dialog .o_form_button_cancel`);
    await animationFrame();
    await click(`.o_helpdesk_team_dashboard button [data-icon="settings"]`);
    await animationFrame();
    expect(`.o-main-components-container .o_dialog .o_form_view`).toHaveCount(1);
    expect(
        `.o-main-components-container .o_dialog .o_form_view [name='id'] span`
    ).toHaveCount(1);
    expect(
        `.o-main-components-container .o_dialog .o_form_view [name='id'] span`
    ).toHaveText("3");
});
