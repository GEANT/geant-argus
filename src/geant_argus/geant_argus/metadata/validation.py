import json
import typing
from django.http import HttpRequest, JsonResponse
import jsonschema
from .schema import METADATA_SCHEMAS


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

        if payload["metadata"].get("version") not in METADATA_SCHEMAS:
            return JsonResponse(
                {
                    "message": (
                        f"metadata must be one of version: {', '.join(METADATA_SCHEMAS.keys())}"
                    )
                },
                status=400,
            )
        schema = METADATA_SCHEMAS[payload["metadata"]["version"]]
        try:
            jsonschema.validate(payload["metadata"], schema)
        except jsonschema.ValidationError as e:
            return JsonResponse({e.json_path.replace("$", "metadata", 1): e.message}, status=400)
