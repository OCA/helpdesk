This modules allows to get a ticket back to its first state when a message is
received about it.


When you are in a non-production environment, you can reopen the ticket with
a simple message as well. It is useful to test the module's function without 
preparing a fake mail environment.

There is a function MailMessage.is_production_env() allowing to define how you
select if you are in production or not. (With a check on the URL for instance)
