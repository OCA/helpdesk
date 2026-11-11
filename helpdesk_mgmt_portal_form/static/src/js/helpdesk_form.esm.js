/* Fetch and inject the per-category question form in the helpdesk portal. */
import {
    evaluateConditions,
    validateRequiredChoices,
} from "@helpdesk_mgmt_portal_form/js/helpdesk_form_conditions.esm";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HelpdeskTicketForm = publicWidget.Widget.extend({
    selector: "form[action='/submitted/ticket']",
    events: {
        "change select[name='category']": "_onChangeCategory",
        change: "_onFormChange",
    },

    start() {
        this._container = this.el.querySelector("#helpdesk_form_questions");
        this._descriptionGroup = this.el.querySelector("#helpdesk_description_group");
        this._descriptionField = this.el.querySelector("textarea[name='description']");
        // A category may be preselected (e.g. browser autofill) on page load.
        const categorySelect = this.el.querySelector("select[name='category']");
        if (categorySelect && categorySelect.value) {
            this._loadForm(categorySelect.value);
        }
        return this._super(...arguments);
    },

    _onChangeCategory(ev) {
        this._loadForm(ev.currentTarget.value);
    },

    async _loadForm(categoryId) {
        if (!this._container) {
            return;
        }
        if (!categoryId) {
            this._showForm("");
            return;
        }
        const response = await fetch(`/ticket/form/${encodeURIComponent(categoryId)}`, {
            headers: {"X-Requested-With": "XMLHttpRequest"},
        });
        const html = response.ok ? await response.text() : "";
        this._showForm(html);
    },

    _showForm(html) {
        this._container.innerHTML = html;
        const hasForm = html.trim().length > 0;
        // When a structured form is shown the free-text description is replaced,
        // so it must not stay visible nor block submission as a required field.
        if (this._descriptionGroup) {
            this._descriptionGroup.classList.toggle("d-none", hasForm);
        }
        if (this._descriptionField) {
            this._descriptionField.required = !hasForm;
        }
        this._refresh();
    },

    _onFormChange() {
        this._refresh();
    },

    _refresh() {
        evaluateConditions(this._container);
        validateRequiredChoices(this._container);
    },
});

export default publicWidget.registry.HelpdeskTicketForm;
