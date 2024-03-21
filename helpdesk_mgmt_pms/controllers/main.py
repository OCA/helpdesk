from odoo import http


class Main(http.Controller):
    @http.route("/helpdesk_mgmt_pms/objects", type="http", auth="user")
    def list(self, **kw):
        return http.request.render(
            "helpdesk_mgmt_pms.listing",
            {
                "root": "/helpdesk_mgmt_pms",
                "objects": http.request.env["main"].search([]),
            },
        )

    @http.route('/helpdesk_mgmt_pms/objects/<model("main"):obj>', auth="public")
    def object(self, obj, **kw):
        return http.request.render("helpdesk_mgmt_pms.object", {"object": obj})
