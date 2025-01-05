import {_t} from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.NewTicket = publicWidget.Widget.extend({
    selector: "form[action='/submitted/ticket']",
    events: Object.assign(
        {},
        {
            'change input[name="attachment"]': "_onChangeAttachment",
        }
    ),
    init() {
        this._super(...arguments);
        this.notification = this.bindService("notification");
    },
    _onChangeAttachment(ev) {
        ev.preventDefault();
        // eslint-disable-next-line no-undef
        const attachment_input = document.getElementById("attachment");
        const max_upload_size = attachment_input.getAttribute("max_upload_size");
        // eslint-disable-next-line no-undef
        const dt = new DataTransfer();
        for (const file of attachment_input.files) {
            if (file.size > max_upload_size) {
                var message = `${file.name} file exceed the maximum file size of ${this.humanSize(max_upload_size)}.`;
                this.notification.add(_t(message), {type: "danger"});
            } else {
                dt.items.add(file);
            }
        }
        attachment_input.files = dt.files;
    },

    humanSize(bytes) {
        if (bytes === 0) return "0 Bytes";
        const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        const size = bytes / Math.pow(1024, i);
        return `${size.toFixed(2)} ${sizes[i]}`;
    },
});
