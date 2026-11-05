# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def uninstall_hook(env):
    action = env.ref(
        "helpdesk_mgmt.helpdesk_ticket_dashboard_action", raise_if_not_found=False
    )
    if action:
        action.write(
            {
                "res_model": "helpdesk.ticket.team",
                "view_mode": "kanban,tree,form,pivot",
                "domain": False,
            }
        )
