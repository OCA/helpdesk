/** @odoo-module **/

import {registerInstancePatchModel} from "@mail/model/model_core";

registerInstancePatchModel(
    "mail.composer_view",
    "helpdesk_mgmt/static/src/models/composer_view/composer_view.js",
    {
        /**
         * @override
         */
        _getMessageData() {
            var res = this._super.apply(this, arguments);

            var subject = "";
            if (this.composer.thread.model === "helpdesk.ticket") {
                subject = "Re:" + this.composer.thread.__values.name;
            }
            res.subject = subject;

            return res;
        },
    }
);
