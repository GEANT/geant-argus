import pathlib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.template import engines, loader
from django.template.context import make_context


class Command(BaseCommand):
    help = """\
Uses the template specified in the TAILWIND_CONFIG_TEMPLATE setting (default: tailwind.config.js)
to dynamically build a tailwind.config.js in the current directory. The template should contain a
'{{ tailwind_content }}' section inside square brackets that will be popuplated by all current
template dirs so that tailwindcss can scan them all for used tailwind classes
"""
    CONFIG_FILENAME = "tailwind.config.js"

    def handle(self, *args, **options):
        template = getattr(settings, "TAILWIND_CONFIG_TEMPLATE", self.CONFIG_FILENAME)

        context = {
            "tailwind_content": "\n".join(
                f"        '{d}/**/*.html'," for d in self.get_template_dirs()
            )
        }
        pathlib.Path(self.CONFIG_FILENAME).write_text(
            self.render_config(template_name=template, context=context)
        )

        self.stdout.write(f"Wrote tailwind config to '{self.CONFIG_FILENAME}'")

    @staticmethod
    def render_config(template_name: str, context):
        template = loader.get_template(template_name)
        return template.template.render(make_context(context, autoescape=False))

    @staticmethod
    def get_template_dirs():
        for engine in engines.all():
            yield from getattr(engine, "template_dirs", [])
