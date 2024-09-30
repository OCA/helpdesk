# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def convert_sale_order_tickets(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["sale.order"],
        "sale_order",
        "ticket_ids",
        "ticket_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_sale_order_tickets(env)
