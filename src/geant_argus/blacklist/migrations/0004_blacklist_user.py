# Generated by Django 5.0.9 on 2024-11-28 09:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.contrib.auth import get_user_model


def set_default_user(apps, schema_editor):
    User = get_user_model()

    Blacklist = apps.get_model("blacklist", "Blacklist")
    Blacklist.objects.update(user=User.objects.get(username="argus"))


def revert_set_default_user(apps, schema_editor):
    Blacklist = apps.get_model("blacklist", "Blacklist")
    Blacklist.objects.update(user=None)


class Migration(migrations.Migration):

    dependencies = [
        ("blacklist", "0003_filter_blacklist_enabled_blacklist_priority_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="blacklist",
            name="user",
            field=models.ForeignKey(
                null=True,
                db_constraint=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="blacklists",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_user, reverse_code=revert_set_default_user),
        migrations.AlterField(
            model_name="blacklist",
            name="user",
            field=models.ForeignKey(
                db_constraint=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="blacklists",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
