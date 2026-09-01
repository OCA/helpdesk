import {loadWysiwygFromTextarea} from "@web_editor/js/frontend/loadWysiwygFromTextarea";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.o_wysiwyg_loader = publicWidget.Widget.extend({
    selector: "textarea.o_wysiwyg_loader",

    start: async function () {
        await this._super(...arguments);
        const options = {
            recordInfo: {
                context: this._getContext(),
                res_model: "helpdesk.ticket",
            },
            resizable: true,
            userGeneratedContent: true,
        };
        await loadWysiwygFromTextarea(this, this.el, options);
    },
});
