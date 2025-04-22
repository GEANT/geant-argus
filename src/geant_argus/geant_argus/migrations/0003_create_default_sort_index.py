from django.db import migrations

ARGUS_APP = "argus_incident"


class Migration(migrations.Migration):
    """Add an index for the default sorting order(see also
    `geant_argus.filter.plugin`). Also includes the default filter (only open
    incidents, which is fully determined by the value of end time) in the in
    """

    dependencies = [
        (ARGUS_APP, "0008_incident_metadata"),
    ]

    operations = [
        migrations.RunSQL(
            (
                f"CREATE INDEX default_sort_index ON {ARGUS_APP}_incident"
                " ((metadata -> 'status') ASC, level ASC, start_time DESC, end_time DESC)"
            ),
            reverse_sql='DROP INDEX "default_sort_index"',
        ),
    ]
