odoo.define('helpdesk_ticket_templates.js', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');

    $(document).ready(function(){
        $("select[name='locations']").trigger('change');
    });

    $("#equipments").hide();
    console.log('xxxxXxxxx');

    $("select[name='locations']").on("change", function (){
        var locations = this;
        var locationssel = locations.options[locations.selectedIndex];

        var equipments_ids = locationssel.getAttribute('equipment_ids');
        if (equipments_ids == null)
            equipments_ids = '';

        console.log('equipments_ids antes:' + equipments_ids);

        equipments_ids = equipments_ids.replace('fsm.equipment', '');
        equipments_ids = equipments_ids.replace('(', '');
        equipments_ids = equipments_ids.replace(')', '');
        equipments_ids = ' ' + equipments_ids + ',';

        console.log('equipments_ids depois:' + equipments_ids);

        var equipments = document.getElementById("equipments");

        Array.from(equipments.getElementsByTagName('option')).forEach(function(element){
            element.hidden = (equipments_ids.indexOf(' ' + element.value + ',') == -1);
        });

        equipments.selectedIndex = -1;
        $("#equipments").show();
    });
});
