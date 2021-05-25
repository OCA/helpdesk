#. Go to *Contact* to see the partners.
#. Edit or create a new partner.
#. Fill in the *Helpdesk Ticket Sequence* field with an existing sequence or create a new one.
#. Go to *Helpdesk > Tickets > Create* to see the form.
#. In the *Contact* field select the partner that has the related sequence.
#. When saved, the next ticket number in the sequence will be generated.

- Notes:
    * Use the contact ticket sequence, if defined. There's a validation if sequence company doesn't match with ticket company, in that case sequence is ignored.
    * If the contact hasn't associated sequence, try the same with parent contact (company of the contact).
    * Then, it's possible to use a general custom sequence for a contact company and its contacts, and for a certain contact of this company use another specific sequence.
