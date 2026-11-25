def post_init_hook(env):
    env["ir.model.fields"].formbuilder_whitelist(
        "helpdesk.ticket",
        [
            "name",
            "description",
            "partner_name",
            "partner_email",
            "category_id",
            "team_id",
        ],
    )
