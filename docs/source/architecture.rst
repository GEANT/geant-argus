Architecture
============

Geant Argus is set up so that it is only loosly coupled to the
`trap processing pipeline <https://swd-documentation.geant.org/dashboard-v3-python/develop/correlator/index.html>`_
(which has Correlator as its endpoint). Geant Argus consists of a number of components that are
shown schematically in the following diagram.

.. only:: drawio

   .. drawio-image:: diagrams/architecture-overview.drawio
      :page-name: architecture

All Geant Argus components are located in the ``noc-alarms-ui`` block. They are: Argus Notifier,
Argus Server and an Alarms API.

Argus Notifier
--------------

The primary connector between the Correlator's AlarmsDB and Geant Argus is the
:ref:`Argus Notifier <argus-notifier>`. Argus Notifier listens on the ``dashbboard.notifications``
RabbitMQ exchange for updates to alarms. It then fetches the alarm's data from the AlarmsDB and
transforms the alarm into an incident. It creates a new incident or updates an existing incident
for the alarm in Geant Argus. Periodically it performs a full synchronization to ensure consistency
between the two databases. It uses the :argus:`Argus API <reference/api.html>` to update
incidents. It only updates incidents on the Argus side, AlarmsDB is considered the source
of truth for alarms.

Argus Server / Geant Argus
--------------------------

The main component of Geant Argus is of course the Django instance running Argus Server / Geant
Argus. It hosts the web frontend as well as the Argus API to interact with incidents, filters and
blacklists. Most of documentation website concerns this component.


.. _back-synchronization:

Alarms API (Back synchronization)
---------------------------------

In general, the AlarmsDB is the single source of truth when in comes to alarms. Argus Notifier
makes sure that the data in Geant Argus matches the source data in AlarmsDB. However, sometimes it
is necessary to update AlarmsDB from events coming from Geant Argus. This happens when a user
updates an alarms with one of the following:

* Add a comment
* Add or update a ticket number
* Clear an alarm with an optional clear time
* Close an alarm

.. note::
  Alarm acknowledgements used to be stored in AlarmsDB. However, there is no longer a reason keep
  a record of them in AlarmsDB. This is an exception to the rule that the AlarmsDB is the
  single source of truth for alarms.

When a user performs one of these actions, the Alarms API is called which updates the AlarmDB. Only
after the Alarms API has sucessfully returned, is the Argus database updated. This way it can be
ensured that the state of the alarm is consistent with what the user sees. See also the diagram
below

.. only:: drawio

   .. drawio-image:: diagrams/back-synchronization.drawio
      :page-name: back-synchronization

There is one theoretical chance of a temporary database inconsistency, and that is if the update
to AlarmsDB (through the API) succeeds, but the write to the Argus database fails. In that case
the user thinks that the action has failed, while in fact it has succeeded. However, the next time
Argus Notifier updates the incident, which will happen during the next synchronization at latest
but may come before that, the incident will be updated with the actual state.