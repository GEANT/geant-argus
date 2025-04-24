User Preferences
================

Argus has a system for managing user specific preferences. These are preferences that a user can
change by navigating to the ``/user/`` page. Some of these preferences are managed by
``argus-server``, while others are defined by ``geant-argus``. The Geant Argus specific preferences
are describe below


Geant Argus Preferences
-----------------------

.. _preferences-aural-alert:

Aural Alert
~~~~~~~~~~~

Whenever a new (pending) incident comes in, Geant Argus may play a notification sound. The sounds
must be ``.mp3`` files located in ``src/geant_argus/geant_argus/static/alerts``. Which sounds can
be chosen is by a user and which is the default value is governed by the
``NEW_INCIDENT_AURAL_ALERTS`` and ``NEW_INCIDENT_AURAL_ALERTS_DEFAULT`` setting. The default is
``off`` to play no sound.


.. _preferences-ack-reminder:

Ack Reminder
~~~~~~~~~~~~

A user can configure Geant Argus to start flashing the acknowledgement checkbox when an incident is
not acknowledgement within a certain timespan in minutes after the start time of the incident. The
valid choices for this preference and the default value is goverened by the 
``ACK_REMINDER_MINUTES`` and ``ACK_REMINDER_MINUTES_DEFAULT`` setting. The default value is
``never`` to disable flashing.

Adding a new preference
-----------------------

Instructions for how to add a new preferences can be found in
:argus:`Argus Documentation: How to add more preferences <development/howtos/add-more-preferences.html>`.
The Geant Argus specific preferences can be found in the ``geant_argus.geant_argus.models`` module.


