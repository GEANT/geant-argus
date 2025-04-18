.. _argus-notifier:

Argus Notifier
==============

Argus Notifier is responsible for detecting changes to the alarms in AlarmsDB and making sure that
the state of the alarms is synchronized to Geant Argus. It does this in two ways. The first is
by listening to the ``dashboard.notification`` exchange to which correlator publishes a message any
time a trap is processed or an alarm changes. The second is by periodically fully synchronizing
relevant alarms in the AlarmsDB with Geant Argus. This is triggered during regular message
handling.

In order to prevent race conditions, especially during synchronization, there is always just one
Argus Notifier process active. This is achieved through RabbitMQ's
`Single Active Consumer <https://www.rabbitmq.com/docs/consumers#single-active-consumer>`_
feature which ensures that only one queue consumer is being served messages at a time.

Message handling
----------------

The message handling flow is given below:

.. only:: drawio

   .. drawio-image:: diagrams/argus-notifier-flow.drawio
      :page-name: argus-notifier-flow

When a notification message is received, Argus Notifier first checks whether a full
:ref:`argus-notifier-synchronization` is due and performs this synchronization if necessary. It
then continues to processing the message:

* Does the alarm exist in the database? If not it is a devoured alarm, we remove the incident in
  Argus
* Load all endpoints and other information concerning the alarm from the AlarmsDB.
* Compile the incident data and `argus-incident-metadata`_ from the alarm data. Some
  information is not available in the AlarmsDB and in some cases the AlarmsDB is not yet updated.
  For these parts we use information in the notifcation message. This concerns:

   * When an alarm clears/closes:

     * Status
     * End time / duration
     * Description (For short lived alarms)

   * Which alarms have been devoured/coalesced by this alarm?

* Check whether this is a new alarm or existing alarm and create or update an
  existing incident.
* Close the incident if needed
* Delete devoured and coalesced incidents. Only the latest (ie. parent) alarm of a coalesced alarm
  group has an associated incident


.. _argus-notifier-synchronization:

Synchronization
---------------

Periodically (by default 5 minutes), Argus Notifier will synchronize all relevant alarms with Geant
Argus. Relevant alarms are alarms that fall into one of the following categories

 * Alarms that are ACTIVE or CLEAR
 * Alarms that have an open incident
 * Alarms that have an incident that has closed less than 30 days ago

Furthermore, only alarms that are the parent of their alarm group (``id==ref_id``) or that do not
have an alarm group yet (for pending alarms) can be relevant.

Synchronization will otherwise update incidents in the same as regular message handling.


.. _argus-incident-metadata:

Incident Metadata
-----------------

Argus incidents by default only contain limited contextual information about the incident contents.
They only have a description that can contain some detailed information. The rest is all agnostic
data such as a start time and a reference url to an external ticketing system. Luckily, the Argus
datamodel also contains a ``metadata`` field for incidents which can contain arbitrary (json) data.

Geant Argus uses this ``metadata`` field extensively to provide the UI with the necessary data for
displaying alarms/incidents properly to the GÉANT NOC. The ``metadata`` schema is versioned. This
is done to be able to detect whether the metadata for a specific incident can be used to render
alarm details and to provide backwards compatibility where possible. An incident's metadata version
is given in the ``version`` field at the root of the ``metadata`` dictionary. As of April 2025, the
latest metadata version is ``v1``. The schema can be found in the
``src/geant_argus/geant_argus/metadata/schema.py`` file.

