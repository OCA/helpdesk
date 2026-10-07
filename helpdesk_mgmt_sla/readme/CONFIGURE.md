To configure this module, you need to:

1.  Allow SLA for a Helpdesk's Team (*Use SLA*)
2.  Set a resource calendar

## Configure SLA

1.  Go to Helpdesk \> Configuration \> SLA.
2.  Edit or create a new SLA.
3.  Select a days or hours for that SLA.
4.  Restrict it with Teams, Categories and Tags (leave empty to apply
    to all). The Filter domain is applied in addition to these, and its
    record count ignores them.
5.  Select the *Stage* the ticket must reach to accomplish the SLA. The
    SLA is accomplished as soon as the ticket is in this stage or a
    later one (by stage sequence). Until then it is in progress, and it
    expires if the deadline passes first.
6.  Optionally select *Ignore Stages*. While the ticket is in one of
    these stages (e.g. "Waiting for customer"), the SLA is on hold and
    its time does not count.

SLAs are computed when a ticket is created, so existing tickets need
*Set SLA* to get newly created SLAs.
