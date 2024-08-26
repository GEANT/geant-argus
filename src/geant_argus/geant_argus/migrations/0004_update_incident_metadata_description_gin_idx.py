from django.db import migrations

ARGUS_APP = "argus_incident"


class Migration(migrations.Migration):
    """Update description index to be UPPER because django uses `UPPER LIKE` instead of `ILIKE` for
    `__icontains` lookups
    """

    dependencies = [
        ("geant_argus", "0002_incident_metadata_description_gin_idx"),
        ("geant_argus", "0003_create_default_sort_index"),
    ]

    operations = [
        migrations.RunSQL(
            [
                'DROP INDEX "metadata_description_gin_idx"',
                (
                    f'CREATE INDEX "metadata_description_gin_idx" ON "{ARGUS_APP}_incident"'
                    " USING gin (UPPER(\"metadata\" ->> 'description') gin_trgm_ops)"
                ),
            ],
            reverse_sql=[
                'DROP INDEX "metadata_description_gin_idx"',
                (
                    f'CREATE INDEX "metadata_description_gin_idx" ON "{ARGUS_APP}_incident"'
                    " USING gin ((\"metadata\" ->> 'description') gin_trgm_ops)"
                ),
            ],
        ),
    ]
