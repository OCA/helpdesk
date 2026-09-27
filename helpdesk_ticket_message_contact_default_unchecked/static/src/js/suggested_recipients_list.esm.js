/* Copyright 2026 Solvos - Iria Alonso
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/
import {SuggestedRecipientsList} from "@mail/core/web/suggested_recipient_list";
import {patch} from "@web/core/utils/patch";

patch(SuggestedRecipientsList.prototype, {
    get suggestedRecipients() {
        const recipients = super.suggestedRecipients;
        if (this.props.thread?.model === "helpdesk.ticket") {
            for (const recipient of recipients) {
                recipient.checked = false;
            }
        }
        return recipients;
    },
});
