import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

registry.category("discuss.channel_commands").add("ticket", {
    help: _t("Create a new ticket (/ticket ticket title)"),
    methodName: "execute_command_ticket",
});
