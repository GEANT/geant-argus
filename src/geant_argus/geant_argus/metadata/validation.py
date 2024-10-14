import json
import typing
from django.http import HttpRequest, JsonResponse
import jsonschema
from .schema import METADATA_SCHEMAS


def validate_metadata(metadata: dict):
    if metadata.get("version") not in METADATA_SCHEMAS:
        return {
            "message": (f"metadata must be one of version: {', '.join(METADATA_SCHEMAS.keys())}")
        }
    schema = METADATA_SCHEMAS[metadata["version"]]

    try:
        jsonschema.validate(metadata, schema)
    except jsonschema.ValidationError as e:
        return {e.json_path.replace("$", "metadata", 1): e.message}


class MetadataValidationMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(
        self, request: HttpRequest, view_func: typing.Callable, view_args, view_kwargs
    ):
        if (
            view_func.__name__ != "IncidentViewSet"
            or request.method not in ("POST", "PUT", "PATCH")
            or request.content_type != "application/json"
        ):
            return

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return

        if not isinstance(payload, dict) or "metadata" not in payload:
            return
        error_message = validate_metadata(payload["metadata"])
        if error_message:
            return JsonResponse(error_message, status=400)
