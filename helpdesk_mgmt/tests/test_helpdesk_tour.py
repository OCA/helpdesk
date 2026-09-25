from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "test_helpdesk_tour")
class TestHelpdeskTour(HttpCase):
    def test_helpdesk_tour(self):
        self.start_tour(
            "/new/ticket",
            "test_helpdesk_tour",
            login="demo",
            timeout=120,
            step_delay=500,
        )
