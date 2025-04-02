Introduction
============

Geant Argus is the (as of 2025) new UI for the NOC Dashboard. It is based on `Argus`_ with
a number of customizations to implement the specific features that are required by the GEANT NOC.


History
-------

The Norwegian NREN SIKT has developed Argus as a generic incident aggregation system. Incidents
from various sources can be ingested into Argus and displayed in a single dashboard. Argus is
designed to be source-agnostic, meaning that it can only display generic information about
incidents, such as a description or a reference to a ticketing system. In 2024 SIKT was looking to
develop a new frontend for Argus. At the same time, GEANT had the ambition of creating a new
dashboard user interface. SIKT and GEANT came together to build a new Argus frontend together.
There was however, a challenge: GEANT needed extra features and information to be shown that were
very specific to Correlator Alarms. SIKT was not in the position to build these features
themselves. However, GEANT and SIKT decided to split the effort:  SIKT would be responsible for
creating the basic UI for displaying alarms/incidents. They would also make sure that the UI is
extensible. This allows GEANT to build upon this base layer with the bespoke features that the
GEANT NOC required. GEANT calls its final product "Geant Argus".

.. note::
  Throughout this documentation both Argus and Geant Argus will be mentioned. Argus refers to the
  SIKT Argus project, while Geant Argus will mean the GEANT specific flavour of Argus


Argus as Django apps
--------------------

Argus is written in `Django`_, a Python web framework that works with a concept called "(reusable)
apps". A Django App is a collection of files (python modules, html templates) that belongs together
and forms a logical piece of functionality. This package can then be distributed on PyPI or other
package repositories. An aspect of Apps that is very beneficial to Geant Argus is the possibility
to override and extend behaviour of apps. This way the ``geant_argus`` app can modify the behaviour
of the (various) ``argus`` app(s).


External links to Documentation
-------------------------------

.. list-table::

   * - Argus
     - `https://argus-server.readthedocs.io/ <https://argus-server.readthedocs.io/>`_
   * - Django
     - `https://docs.djangoproject.com/ <https://docs.djangoproject.com/>`_
   * - Django Tutorial
     - `https://docs.djangoproject.com/en/5.1/intro/tutorial01/ <https://docs.djangoproject.com/en/5.1/intro/tutorial01/>`_

.. _Argus: https://github.com/Uninett/Argus/
.. _Django: https://github.com/Uninett/Argus/