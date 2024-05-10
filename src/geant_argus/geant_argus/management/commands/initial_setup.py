from argus.dev.management.commands import initial_setup
from argus.auth.models import User
from argus.incident.models import SourceSystem, SourceSystemType


class Command(initial_setup.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--correlator-password",
            type=str,
            help="Set a password for the correlator. Default: long random string",
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)

        password = options.get("correlator_password", None)
        user = self.try_create_correlator_user(specified_password=password)
        sst, _ = SourceSystemType.objects.get_or_create(name="correlator")
        ss, _ = SourceSystem.objects.get_or_create(name="correlator", type=sst, user=user)

    def try_create_correlator_user(self, username="correlator", specified_password=None):
        password = specified_password or initial_setup.generate_password_string()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create(
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
        else:
            msg = f"User {username} already exists!"
            self.stderr.write(self.style.WARNING(msg))
        return user
