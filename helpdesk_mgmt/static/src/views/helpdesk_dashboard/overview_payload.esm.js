/** @odoo-module **/

/**
 * Maps the OCA overview RPC payload to the banner template state shape.
 *
 * @param {Record<string, any>} api
 */
export function overviewApiToBannerState(api) {
    const assigned = api.assigned_open || {};
    const closed = api.assigned_closed || {};
    const bucket = (key) => ({
        count: assigned[key]?.ticket_count ?? 0,
        hours: assigned[key]?.mean_open_hours ?? 0,
    });
    return {
        show_demo: Boolean(api.sample_mode),
        my_all: bucket("any"),
        my_high: bucket("high"),
        my_urgent: bucket("urgent"),
        today: {count: closed.today ?? 0},
        "7days": {count: closed.last_7_days ?? 0},
    };
}
