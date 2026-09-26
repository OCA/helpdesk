/* Pure DOM helpers for the portal helpdesk form: conditional display and
 * "at least one option" validation. Kept free of the public widget so they can
 * be unit-tested in isolation. */
import {_t} from "@web/core/l10n/translation";

function triggerMatches(question, container) {
    const triggerId = question.dataset.triggerQuestion;
    const triggerType = question.dataset.triggerType;
    let expected = [];
    try {
        expected = JSON.parse(question.dataset.triggerValues || "[]");
    } catch {
        expected = [];
    }
    const inputs = container.querySelectorAll(`[name='answer_${triggerId}']`);
    const submitted = [];
    for (const input of inputs) {
        // A disabled trigger belongs to a hidden question, so it cannot
        // satisfy the condition (conditions cascade).
        if (input.disabled) {
            continue;
        }
        if (input.tagName === "SELECT") {
            if (input.value) {
                submitted.push(input.value);
            }
        } else if (input.type === "checkbox") {
            if (triggerType === "boolean") {
                submitted.push(input.checked ? "Yes" : "No");
            } else if (input.checked) {
                submitted.push(input.value);
            }
        }
    }
    return expected.some((value) => submitted.includes(value));
}

/**
 * Show or hide conditional questions based on the current answers, and disable
 * hidden ones so they neither submit nor block native validation. Runs several
 * passes so chained conditions settle.
 */
export function evaluateConditions(container) {
    const questions = container.querySelectorAll(
        ".o_helpdesk_question[data-conditional='1']"
    );
    if (!questions.length) {
        return;
    }
    let changed = true;
    let pass = 0;
    while (changed && pass < 10) {
        changed = false;
        pass += 1;
        for (const question of questions) {
            const visible = triggerMatches(question, container);
            if (question.classList.contains("d-none") === visible) {
                changed = true;
            }
            question.classList.toggle("d-none", !visible);
            question.querySelectorAll("input, select, textarea").forEach((input) => {
                input.disabled = !visible;
            });
        }
    }
}

/**
 * Enforce "at least one option" on required multiple-choice questions. Native
 * `required` can only force a single checkbox, so the rule is applied through
 * the Constraint Validation API on the first checkbox of the group, which
 * blocks submission while none is ticked.
 */
export function validateRequiredChoices(container) {
    const groups = container.querySelectorAll(
        ".o_helpdesk_question[data-require-choice='1']"
    );
    for (const group of groups) {
        const boxes = group.querySelectorAll("input[type='checkbox']");
        if (!boxes.length) {
            continue;
        }
        // A hidden conditional group has disabled inputs and is skipped by
        // native validation, so it must not be reported as invalid.
        const active = !boxes[0].disabled;
        const anyChecked = Array.from(boxes).some((box) => box.checked);
        boxes[0].setCustomValidity(
            active && !anyChecked ? _t("Please select at least one option.") : ""
        );
    }
}
