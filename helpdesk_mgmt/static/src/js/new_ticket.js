odoo.define("helpdesk_mgmt.new_ticket", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    var core = require("web.core");
    var utils = require("web.utils");
    var _t = core._t;

    publicWidget.registry.NewTicket = publicWidget.Widget.extend({
        selector: "form[action='/submitted/ticket']",
        events: {
            'change input[name="attachment"]': "_onChangeAttachment",
        },
        _onChangeAttachment(ev) {
            ev.preventDefault();
            const attachment_input = document.getElementById("attachment");
            const max_upload_size = attachment_input.getAttribute("max_upload_size");
            const dt = new DataTransfer();
            for (const file of attachment_input.files) {
                if (file.size > max_upload_size) {
                    this.displayNotification({
                        title: _t("File upload"),
                        message: _.str.sprintf(
                            _t("%s file exceed the maximum file size of %s."),
                            file.name,
                            utils.human_size(max_upload_size)
                        ),
                        type: "danger",
                    });
                } else {
                    dt.items.add(file);
                }
            }
            attachment_input.files = dt.files;
        },
    });
});
