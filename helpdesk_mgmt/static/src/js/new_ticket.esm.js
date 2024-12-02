/* eslint no-undef: 0 */
import {_t} from "@web/core/l10n/translation";
import {humanNumber} from "@web/core/utils/numbers";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.NewTicket = publicWidget.Widget.extend({
    selector: "form[action='/submitted/ticket']",
    events: {
        'change input[name="attachment"]': "_onChangeAttachment",
    },
    _onChangeAttachment(ev) {
        ev.preventDefault();
        const attachment_input = document.getElementById("attachment");
        const information_input = document.getElementById("attachment_information");
        information_input.style.display = "none";
        const max_upload_size = parseInt(
            attachment_input.getAttribute("max_upload_size"),
            10
        );
        const dt = new DataTransfer();
        for (const file of attachment_input.files) {
            if (file.size > max_upload_size) {
                information_input.textContent = _t(
                    "The selected file (%sB) is over the maximum allowed file size (%sB).",
                    humanNumber(file.size),
                    humanNumber(max_upload_size)
                );
                information_input.style.display = "";
            } else {
                dt.items.add(file);
            }
        }
        attachment_input.files = dt.files;
    },
});
