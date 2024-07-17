import json
import typing
from django.http import HttpRequest, JsonResponse
import jsonschema
from .schema import METADATA_V0A3_SCHEMA


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

        try:
            jsonschema.validate(payload["metadata"], METADATA_V0A3_SCHEMA)
        except jsonschema.ValidationError as e:
            return JsonResponse({e.json_path.replace("$", "metadata", 1): e.message}, status=400)
