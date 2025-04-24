Collaboration with Sikt
=======================

A good collaboration with Sikt and the developers of Argus in specific is essential for the success
of Geant Argus.

Development
-----------

Argus is in active development. When developing features for Geant Argus it is often useful to not
develop against the Argus ``master`` branch, but against the release running on test. Every Argus
release has an associated git tag, so you can just ``checkout`` or ``switch`` to that tag.

At the same time, it is very useful to keep up to date with the latest changes in Argus and to
preprare for when a new version is released, so it is easy to start supporting that new version
once its out.


Supporting a new version of Argus Server
----------------------------------------

When Sikt releases a new version, often this requires some changes to geant-argus to make use of
those changes, and to make sure that any customizations in geant-argus are compatible with the
new release, such as :ref:`overridden templates <checking-changed-overridden-templates>`. Other
changes that may be required are additional settings, or changing new default settings.

Sometimes, a new release of Argus brings in functionality that Geant Argus also has. This can
offer an opportunity to simplify code in Geant Argus, if the implementation of that functionality
is similar enough to the implementation in Geant Argus.


.. _checking-changed-overridden-templates:

Checking changed overridden templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get a overview of templates that are overridden in Geant Argus that have changed in a new Argus
version you can use the ``templatediff.py`` commmand in the root of the ``geant-argus``
repository. This command take the path to a checked out version the
`Argus repository <https://github.com/Uninett/Argus/>`_ as an argument as well as a git diff
specification. For example, if you have the Argus repo checked out directly next to the
geant-argus repository, and you want to get a list of the changed overridden templates between Argus
v1.34.1 and v1.35.0`` you can run the following command::

  ./templatediff.py ../Argus v1.34.1..v1.35.0

Optionally, to get a full diff of those templates, add the ``--full`` parameter. You can then
compare those changes with the overriding templates in geant-argus to determine if the overrides
are still compatible, or if some additional work is required.


Unused functionality
--------------------

Argus has some functionality that is not used in Geant Argus. These have been hidden from view
in Geant Argus. As of Argus version 1.36.0 They are:

 * Default incident details page
 * Most of the incident list columns
 * Notification profiles

Any changes in Argus server to these parts of the code is generally safe to ignore for Geant Argus
