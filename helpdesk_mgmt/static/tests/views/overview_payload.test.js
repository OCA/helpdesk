import {expect, test} from "@odoo/hoot";
import {overviewApiToBannerState} from "@helpdesk_mgmt/views/helpdesk_dashboard/overview_payload.esm";

test("overview API is adapted to banner state", () => {
    const state = overviewApiToBannerState({
        sample_mode: true,
        assigned_open: {
            any: {ticket_count: 7, mean_open_hours: 24},
            high: {ticket_count: 2, mean_open_hours: 8.5},
            urgent: {ticket_count: 1, mean_open_hours: 11},
        },
        assigned_closed: {today: 2, last_7_days: 11},
    });
    expect(state.show_demo).toBe(true);
    expect(state.my_all).toEqual({count: 7, hours: 24});
    expect(state.today.count).toBe(2);
    expect(state["7days"].count).toBe(11);
});

test("overview API handles missing buckets", () => {
    const state = overviewApiToBannerState({sample_mode: false});
    expect(state.show_demo).toBe(false);
    expect(state.my_all).toEqual({count: 0, hours: 0});
    expect(state.my_high).toEqual({count: 0, hours: 0});
    expect(state.my_urgent).toEqual({count: 0, hours: 0});
    expect(state.today).toEqual({count: 0});
    expect(state["7days"]).toEqual({count: 0});
});
