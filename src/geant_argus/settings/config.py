import json
import pathlib
import jsonschema


CONFIG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "DEFAULT_FROM_EMAIL": {"type": "string"},
        "SEND_EXPIRED_BLACKLISTS_EMAILS_TO": {"type": "array", "items": {"type": "string"}},
        "SHORT_LIVED_ALARMS_UI_URL": {"type": ["string", "null"]},
    },
    "required": [
        "SEND_EXPIRED_BLACKLISTS_EMAILS_TO",
    ],
}


def load_config(filename, settings=None):
    config = json.loads(pathlib.Path(filename).read_text())
    jsonschema.validate(config, CONFIG_SCHEMA)
    if settings is None:
        return config

    if hasattr(settings, "update") and callable(settings.update):
        settings.update(config)
    else:
        for k, v in config.items():
            setattr(settings, k, v)
