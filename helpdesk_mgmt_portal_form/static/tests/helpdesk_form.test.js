/* Unit tests for the portal helpdesk form conditional-display logic. */
import {describe, expect, test} from "@odoo/hoot";
import {
    evaluateConditions,
    validateRequiredChoices,
} from "@helpdesk_mgmt_portal_form/js/helpdesk_form_conditions.esm";
import {patchTranslations} from "@web/../tests/web_test_helpers";

describe.current.tags("headless");

// ValidateRequiredChoices calls _t(), which requires loaded translations.
patchTranslations();

function buildContainer(html) {
    const container = document.createElement("div");
    container.innerHTML = html;
    return container;
}

const SELECTION_FRAGMENT = `
    <div class="form-group o_helpdesk_question" data-question-id="1">
        <select name="answer_1">
            <option value=""></option>
            <option value="Low">Low</option>
            <option value="High">High</option>
        </select>
    </div>
    <div class="form-group o_helpdesk_question d-none" data-question-id="2"
         data-conditional="1" data-trigger-question="1"
         data-trigger-type="selection" data-trigger-values='["High"]'>
        <input type="text" name="answer_2"/>
    </div>
`;

const BOOLEAN_FRAGMENT = `
    <div class="form-group o_helpdesk_question" data-question-id="3">
        <input type="checkbox" name="answer_3" value="1"/>
    </div>
    <div class="form-group o_helpdesk_question d-none" data-question-id="4"
         data-conditional="1" data-trigger-question="3"
         data-trigger-type="boolean" data-trigger-values='["Yes"]'>
        <input type="text" name="answer_4"/>
    </div>
`;

const REQUIRED_MULTI_FRAGMENT = `
    <div class="form-group o_helpdesk_question" data-question-id="5"
         data-require-choice="1">
        <input type="checkbox" name="answer_5" value="Screen"/>
        <input type="checkbox" name="answer_5" value="Battery"/>
    </div>
`;

describe("helpdesk_mgmt_portal_form conditional display", () => {
    test("selection trigger shows and hides the dependent question", () => {
        const container = buildContainer(SELECTION_FRAGMENT);
        const dependent = container.querySelector('[data-question-id="2"]');
        const select = container.querySelector('select[name="answer_1"]');
        const input = container.querySelector('input[name="answer_2"]');

        evaluateConditions(container);
        expect(dependent).toHaveClass("d-none");
        expect(input.disabled).toBe(true);

        select.value = "High";
        evaluateConditions(container);
        expect(dependent).not.toHaveClass("d-none");
        expect(input.disabled).toBe(false);

        select.value = "Low";
        evaluateConditions(container);
        expect(dependent).toHaveClass("d-none");
        expect(input.disabled).toBe(true);
    });

    test("boolean trigger matches on the checked state", () => {
        const container = buildContainer(BOOLEAN_FRAGMENT);
        const dependent = container.querySelector('[data-question-id="4"]');
        const checkbox = container.querySelector('input[name="answer_3"]');

        evaluateConditions(container);
        expect(dependent).toHaveClass("d-none");

        checkbox.checked = true;
        evaluateConditions(container);
        expect(dependent).not.toHaveClass("d-none");

        checkbox.checked = false;
        evaluateConditions(container);
        expect(dependent).toHaveClass("d-none");
    });
});

describe("helpdesk_mgmt_portal_form required choices", () => {
    test("required multiple choice needs at least one option", () => {
        const container = buildContainer(REQUIRED_MULTI_FRAGMENT);
        const boxes = container.querySelectorAll('input[name="answer_5"]');

        validateRequiredChoices(container);
        expect(boxes[0].checkValidity()).toBe(false);

        boxes[1].checked = true;
        validateRequiredChoices(container);
        expect(boxes[0].checkValidity()).toBe(true);
    });
});
