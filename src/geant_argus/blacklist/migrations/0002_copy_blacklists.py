# Generated by Django 5.0.9 on 2024-11-12 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blacklist", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            """
            INSERT INTO blacklist_blacklist (
                id,
                name,
                message,
                level,
                filter_id
            )
            SELECT
                id,
                name,
                message,
                level,
                filter_id
            FROM
                geant_argus_blacklist;
            SELECT setval(
                pg_get_serial_sequence('"blacklist_blacklist"','id'),
                coalesce(max("id"), 1),
                max("id") IS NOT null)
            FROM "blacklist_blacklist";
        """,
            reverse_sql="""
            INSERT INTO geant_argus_blacklist (
                 id,
                name,
                message,
                level,
                filter_id
            )
            SELECT
                  id,
                name,
                message,
                level,
                filter_id
                category_id
            FROM
                blacklist_blacklist;
            TRUNCATE blacklist_blacklist;
            SELECT setval(
                pg_get_serial_sequence('"blacklist_blacklist"','id'),
                coalesce(max("id"), 1),
                max("id") IS NOT null)
            FROM "blacklist_blacklist";
        """,
        )
    ]