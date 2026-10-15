Overview
========

Allows dynamic control over which contact (partner_id) on ticket,
based on the configuration of the assigned Helpdesk Team (team_id). The logic works as follows:
- If the team has a default contact, it will fill the contact field with that value.
- If the team has a unique contact, only that contact will be available.
- If the team has a list of allowed contacts, only those contacts will be available.
- If the team has no restrictions, all contacts will be available.

Use Case
=================

This module is designed for organizations that structure their Helpdesk teams
around customers, rather than functional support areas.

A typical use case is a software development or services company where:

- Each customer has a dedicated Helpdesk Team.
- Developers and support agents are assigned to customer-specific teams.
- The Helpdesk dashboard is used to track workload per customer
  (e.g. "Customer X – 4 open tickets").

In this setup, every ticket created for a given team is implicitly related
to a specific customer. However, in standard Odoo, both fields must still be
manually selected:

- Team: Customer X
- Customer: Customer X

This repetition is error-prone and slows down ticket creation.

Module Purpose
==============

The goal of this module is to streamline ticket creation and prevent
inconsistent data by linking Helpdesk Teams to one or more allowed customers.

Depending on the team configuration, the module can:

- Automatically set a default customer when a team is selected.
- Restrict the customer field to a single allowed customer.
- Restrict the customer field to a predefined list of customers.

As a result:

- Ticket creation is faster.
- The risk of assigning a ticket to the wrong customer is reduced.
- The Helpdesk dashboard remains consistently grouped by customer.

Design Rationale
================

Why the restriction goes from Team to Customer
---------------------------------------------

Unlike more common setups where customers are restricted to specific teams,
this module addresses scenarios where:

- Teams represent customer contexts.
- Agents frequently switch between customer-dedicated teams.
- Correct customer assignment is critical for reporting, dashboards,
  and contractual scope control.

For these scenarios, enforcing customer consistency at the team level
is both intentional and required.

Why a server-side constraint is required
---------------------------------------

The dynamic domain on the customer field is intended as user guidance,
but it is not sufficient to guarantee data consistency.

In standard Odoo behavior, many2one fields allow on-the-fly record creation.
For example, an agent may type a new customer name and press Enter, creating
a new partner that bypasses the UI domain restriction.

For this reason, a server-side constraint is required to ensure that,
when a Helpdesk Team defines an explicit list of allowed customers,
no ticket can be saved with a customer outside that list.

The constraint does not prevent customer creation; it only enforces
the team-to-customer consistency rule at persistence time.

Why Record Rules are not used
----------------------------

This module does not aim to restrict global access to partners.

Partner availability is contextual and depends on the Helpdesk Team selected
on each ticket. The same user may work with multiple customer-dedicated teams
during the same day.

Record Rules are evaluated at user or group level and are therefore not
well suited for per-record, team-dependent restrictions.

For this reason, the module uses:
- a dynamic domain for user guidance
- a server-side constraint for data consistency

This keeps the implementation simple, predictable, and aligned with
Odoo’s standard interaction patterns.
