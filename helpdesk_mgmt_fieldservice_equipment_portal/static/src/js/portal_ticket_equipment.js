/* Copyright (C) 2026 Popsolutions
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 * Filtra o select de equipamentos pela localização escolhida em /new/ticket. */
document.addEventListener("DOMContentLoaded", function () {
    const locationSelect = document.getElementById("ticket_location");
    const equipmentSelect = document.getElementById("ticket_equipment");
    if (!locationSelect || !equipmentSelect) {
        return;
    }
    locationSelect.addEventListener("change", function () {
        const selectedLocation = locationSelect.value;
        for (const option of equipmentSelect.options) {
            if (!option.value) {
                continue;
            }
            const isVisible =
                !selectedLocation || option.dataset.location === selectedLocation;
            option.hidden = !isVisible;
            option.disabled = !isVisible;
        }
        const current = equipmentSelect.selectedOptions[0];
        if (current && current.value && current.hidden) {
            equipmentSelect.value = "";
        }
    });
});
