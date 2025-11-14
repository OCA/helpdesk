/** @odoo-module **/

import {insert} from "@mail/model/model_field_command";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "MessagingInitializer",
    recordMethods: {
        /**
         * @override
         */
        _initCommands() {
            this._super();
            this.messaging.update({
                commands: insert({
                    help: this.env._t("Create a new ticket (/ticket ticket title)"),
                    methodName: "execute_command_ticket",
                    name: "ticket",
                }),
            });
        },
    },
});
