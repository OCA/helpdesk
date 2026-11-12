When opening a helpdesk ticket from the portal, the customer picks the
equipment concerned (optionally filtering by location first — plain JS, no
extra dependencies).

Hardening built in:

- only equipments owned by the logged user's commercial partner are listed
  and accepted (a forged submission with someone else's equipment is
  silently ignored);
- the ticket's FSM location is derived server-side from the equipment,
  satisfying the location/equipment consistency constraint of
  `helpdesk_mgmt_fieldservice_equipment`.

The backend ticket list gets an optional **Equipment** column and a group-by
filter.
