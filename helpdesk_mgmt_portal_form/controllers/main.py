# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskTicketFormController(HelpdeskTicketController):
    def _get_portal_form(self, category_id):
        """Return the form to render for a portal category, or an empty recordset.

        The form is only served when the company actually exposes categories in
        the portal and the category is portal-visible, so it can never be probed
        for categories that are not meant to be selectable.
        """
        if (
            not category_id
            or not request.env.company.helpdesk_mgmt_portal_select_category
        ):
            return request.env["helpdesk.ticket.form"]
        category = (
            request.env["helpdesk.ticket.category"]
            .sudo()
            .browse(category_id)
            .exists()
            .filtered(lambda c: c.show_in_portal)
        )
        return category.form_id

    @http.route(
        "/ticket/form/<int:category_id>",
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def get_ticket_form(self, category_id, **kw):
        """Return the rendered questions fragment for a portal category.

        Responds with an empty body when the category has no form, so the JS
        clears the container and the standard description textarea takes over.
        """
        form = self._get_portal_form(category_id)
        if not form:
            return request.make_response("")
        return request.render(
            "helpdesk_mgmt_portal_form.portal_form_questions", {"form": form}
        )

    def _get_answer_values(self, question, form_data):
        """Return the submitted value(s) of a question as a list of strings."""
        field_name = f"answer_{question.id}"
        if question.question_type == "multi":
            return [v for v in form_data.getlist(field_name) if v]
        if question.question_type == "boolean":
            return ["Yes"] if form_data.get(field_name) else ["No"]
        value = form_data.get(field_name)
        return [value] if value else []

    def _get_active_questions(self, form, form_data):
        """Return questions actually shown, resolving conditional display.

        Conditions are re-evaluated server-side from the submitted answers so a
        skipped question is never rendered, regardless of what the client sent.
        """
        active_ids = {q.id for q in form.question_ids if not q.is_conditional}
        changed = True
        while changed:
            changed = False
            for question in form.question_ids:
                if question.id in active_ids or not question.is_conditional:
                    continue
                trigger = question.triggering_question_id
                submitted = set(self._get_answer_values(trigger, form_data))
                expected = set(question._get_triggering_values())
                if trigger.id in active_ids and submitted & expected:
                    active_ids.add(question.id)
                    changed = True
        return form.question_ids.filtered(lambda q: q.id in active_ids)

    def _get_submitted_answers(self, form):
        """Collect submitted answers of shown questions as display-ready dicts."""
        form_data = request.httprequest.form
        return [
            {
                "label": question.name,
                "question_type": question.question_type,
                "values": self._get_answer_values(question, form_data),
            }
            for question in self._get_active_questions(form, form_data)
        ]

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        category = request.env["helpdesk.ticket.category"].browse(
            int(kw.get("category") or 0)
        )
        form = category.form_id
        if form:
            answers = self._get_submitted_answers(form)
            vals["description"] = request.env["ir.qweb"]._render(
                "helpdesk_mgmt_portal_form.portal_ticket_description",
                {"form": form, "answers": answers},
            )
        return vals
