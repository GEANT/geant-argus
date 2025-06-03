from django.db import migrations

ARGUS_APP = "argus_incident"


class Migration(migrations.Migration):
    """Change description search to incident.description instead of incident.metadata.description
    """

    dependencies = [
        ("geant_argus", "0004_update_incident_metadata_description_gin_idx"),
    ]

    operations = [
        migrations.RunSQL(
            [
                'DROP INDEX "metadata_description_gin_idx"',
                (
                    f'CREATE INDEX "incident_description_gin_idx" ON "{ARGUS_APP}_incident"'
                    " USING gin (UPPER(description) gin_trgm_ops)"
                ),
            ],
            reverse_sql=[
                'DROP INDEX "incident_description_gin_idx"',
                (
                    f'CREATE INDEX "metadata_description_gin_idx" ON "{ARGUS_APP}_incident"'
                    " USING gin (UPPER(\"metadata\" ->> 'description') gin_trgm_ops)"
                ),
            ],
        ),
    ]
