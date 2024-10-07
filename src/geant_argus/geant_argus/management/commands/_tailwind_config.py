import pathlib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.template import engines
from django.template.context import make_context
from django.template import Template
import sys, os


class Command(BaseCommand):
    help = """\
Uses the template specified in the TAILWIND_CONFIG_TEMPLATE setting (default: tailwind.config.js)
to dynamically build a tailwind.config.js in the current directory. The template should contain a
'{{ tailwind_content }}' section inside square brackets that will be popuplated by all current
template dirs so that tailwindcss can scan them all for used tailwind classes
"""
    DEFAULT_TEMPLATE_PATH = "tailwind.config.template.js"
    DEFAULT_TARGET = "tailwind.config.js"

    def handle(self, *args, **options):
        template_loc = getattr(settings, "TAILWIND_CONFIG_TEMPLATE", self.DEFAULT_TEMPLATE_PATH)
        target_path = getattr(settings, "TAILWIND_CONFIG_TARGET", self.DEFAULT_TARGET)
        context = {
            "tailwind_content": "\n".join(
                f"        '{d}/**/*.html'," for d in self.get_template_dirs()
            )
        }
        template_path = pathlib.Path(template_loc)
        if not template_path.is_file():
            self.stdout.write(f"{template_loc} is not a file")
            return

        pathlib.Path(target_path).write_text(
            self.render_config(template_path=template_path, context=context)
        )

        self.stdout.write(f"Wrote tailwind config to '{target_path}'")

    @staticmethod
    def render_config(template_path: pathlib.Path, context):
        template = Template(template_path.read_text())
        return template.render(make_context(context, autoescape=False))

    @staticmethod
    def get_template_dirs():
        for engine in engines.all():
            yield from getattr(engine, "template_dirs", [])
