from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "stock.move",
                "stock_move",
                "helpdesk_tickets_count",
                "helpdesk_ticket_count",
            ),
            (
                "stock.picking",
                "stock_picking",
                "helpdesk_tickets_count",
                "helpdesk_ticket_count",
            ),
        ],
    )
