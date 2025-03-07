# Generated by Django 5.0.9 on 2024-11-26 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("argus_notificationprofile", "0017_change_event_type_to_event_types"),
        ("blacklist", "0002_copy_blacklists"),
    ]

    operations = [
        migrations.CreateModel(
            name="Filter",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("argus_notificationprofile.filter",),
        ),
        migrations.AddField(
            model_name="blacklist",
            name="enabled",
            field=models.BooleanField(db_default=True, default=True),
        ),
        migrations.AddField(
            model_name="blacklist",
            name="priority",
            field=models.IntegerField(db_default=10, default=10),
        ),
        migrations.AddField(
            model_name="blacklist",
            name="review_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="blacklist",
            name="name",
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name="blacklist",
            name="filter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="blacklists",
                to="blacklist.filter",
            ),
        ),
    ]
