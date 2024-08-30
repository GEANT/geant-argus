from typing import Tuple
from argus.dev.management.commands import initial_setup
from argus.auth.models import User
from argus.incident.models import SourceSystem, SourceSystemType, Acknowledgement
from django.contrib.auth.models import Group, Permission

from django.contrib.contenttypes.models import ContentType


class Command(initial_setup.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--correlator-password",
            type=str,
            help="Set a password for the correlator. Default: long random string",
        )
        parser.add_argument(
            "--servicedesk-password",
            type=str,
            help="Set a password for the service desk account. Default: long random string",
        )
        parser.add_argument(
            "--noc-password",
            type=str,
            help="Set a password for the noc accound. Default: long random string",
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)
        self.configure_correlator_account(password=options.get("correlator_password", None))
        self.configure_ack_account(username="noc", password=options.get("noc_password", None))
        self.configure_ack_account(
            username="servicedesk", password=options.get("servicedesk_password", None)
        )

    def configure_correlator_account(self, password):
        user, _ = self.try_create_user(username="correlator", specified_password=password)
        sst, _ = SourceSystemType.objects.get_or_create(name="correlator")
        ss, _ = SourceSystem.objects.get_or_create(name="correlator", type=sst, user=user)

    def configure_ack_account(self, username, password, groupname=None):
        groupname = groupname or username
        user, created = self.try_create_user(username=username, specified_password=password)
        group, _ = self.try_create_ack_group(groupname)
        if created and group not in user.groups.all():
            user.groups.add(group)

    def configure_service_desk_account(self, options):
        password = options.get("servicedesk_password", None)
        user, created = self.try_create_user(username="servicedesk", specified_password=password)
        if created:
            group, _ = self.try_create_ack_group("servicedesk")
            user.groups.add(group)

    def try_create_user(self, username, specified_password=None) -> Tuple[User, bool]:
        password = specified_password or initial_setup.generate_password_string()

        try:
            user = User.objects.get(username=username)
            msg = f"User {username} already exists!"
            self.stderr.write(self.style.WARNING(msg))
            created = False
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email="",
                first_name=username.capitalize(),
                last_name="",
                password=password,
            )
            if specified_password:
                msg = f'Successfully created user "{user.username}" with the chosen password'
            else:
                msg = f'  Created user "{user.username}" with password "{password}".'
                stars = "*" * len(msg)
                msg = "\n\n".join([stars, msg, stars])

            self.stdout.write(self.style.SUCCESS(msg))
            created = True
        return user, created

    def try_create_ack_group(self, groupname) -> Tuple[Group, bool]:
        group, created = Group.objects.get_or_create(name=groupname)
        if created:
            content_type = ContentType.objects.get_for_model(Acknowledgement)
            permissions = (
                Permission.objects.get(
                    codename=f"{perm_action}_acknowledgement", content_type=content_type
                )
                for perm_action in ("add", "change", "view", "delete")
            )
            group.permissions.add(*permissions)
            self.stdout.write(self.style.SUCCESS(f"Successfully created group {groupname}"))
        else:
            self.stderr.write(self.style.WARNING(f"Group {groupname} already exists!"))
        return group, created
