import dataclasses
from datetime import datetime
import itertools


@dataclasses.dataclass
class Operator:
    template: str

    def __init__(self, name: str, display_name: str = None):
        self.name = name
        self.display_name = display_name if display_name is not None else name

    def initial_value(self):
        raise NotImplementedError

    def parse_formdata(self, form_data: dict, prefix: str):
        raise NotImplementedError


class TextOperator(Operator):
    template = "geant/filters/_filter_text_input.html"

    def initial_value(self):
        return {"value": ""}

    def parse_formdata(self, form_data: dict, prefix):
        return {"value": form_data.get(prefix + "val:str", "")[:100]}


class BooleanOperator(Operator):
    template = "geant/filters/_filter_boolean_input.html"

    def initial_value(self):
        return {"value": True}

    def parse_formdata(self, form_data: dict, prefix: str):
        raw = form_data.get(prefix + "val:bool", "true")
        return {"value": raw == "true"}


class DateTimeOperator(Operator):
    NORMALIZED_DATETIME = "%Y-%m-%dT%H:%M"
    template = "geant/filters/_filter_datetime_picker.html"

    def initial_value(self):
        return {"value": datetime.now().strftime(self.NORMALIZED_DATETIME)}

    def parse_formdata(self, form_data: dict, prefix: str):
        raw = form_data.get(prefix + "val:datetime", "")
        try:
            datetime.strptime(raw, self.NORMALIZED_DATETIME)
        except ValueError:
            raw = datetime.now().strftime(self.NORMALIZED_DATETIME)
        return {"value": raw}


class TimeDeltaOperator(Operator):
    units = ("minutes", "hours", "days", "weeks")
    template = "geant/filters/_filter_timedelta_picker.html"

    def initial_value(self):
        return {"days": 1}

    def parse_formdata(self, form_data: dict, prefix: str):
        raw_amount = form_data.get(prefix + "val:timedelta", "1")
        try:
            amount = max(1, int(raw_amount))
        except ValueError:
            amount = 1

        raw_unit = form_data.get(prefix + "unit", "days")
        unit = raw_unit if raw_unit in self.units else "days"

        return {"value": amount, "unit": unit}


@dataclasses.dataclass
class FilterField:
    name: str
    display_name: str
    operators: list[Operator]

    def __post_init__(self):
        self.operators_by_name = {op.name: op for op in self.operators}

    def default_rule(self):
        operator = self.operators[0]
        return {
            "type": "rule",
            "field": self.name,
            "operator": operator.name,
            **operator.initial_value(),
        }

    def parse_form_data(self, form_data, prefix: str):
        op_str = form_data.get(prefix + "op")
        if op_str not in self.operators_by_name:
            op = self.operators[0]
            return {"type": "rule", "field": self.name, "operator": op.name, **op.initial_value()}

        op = self.operators_by_name[op_str]
        return {
            "type": "rule",
            "field": self.name,
            "operator": op.name,
            **op.parse_formdata(form_data, prefix=prefix),
        }

    def render(self, value) -> str:
        pass


class ComplexFilter:
    version = "v1"

    def __init__(self, fields: list[FilterField]):
        self.fields = fields
        self.fields_by_name = {field.name: field for field in self.fields}

    def default_rule(self):
        field = self.fields[0]
        return field.default_rule()

    def parse_form_data(self, form_data: dict) -> dict:
        return {
            "version": self.version,
            **self._parse_formdata_helper(form_data, prefix=""),
        }

    def _parse_formdata_helper(self, form_data: dict, prefix: str) -> dict:
        if try_field := form_data.get(prefix + "field"):
            if try_field in ("or", "and"):
                return {"type": "group", "operator": try_field, "items": [self.default_rule()]}
            field = self.fields_by_name.get(try_field, self.fields[0])
            return field.parse_form_data(form_data, prefix=prefix)

        if (try_field := form_data.get(prefix + "op")) is not None:
            if try_field not in ("or", "and"):
                field = self.fields_by_name.get(try_field, self.fields[0])
                return field.default_rule()
            result = {"type": "group", "operator": try_field, "items": []}
            for idx in itertools.count():
                new_prefix = f"{prefix}{idx}_"
                parsed = self._parse_formdata_helper(form_data, prefix=new_prefix)
                if parsed is None:
                    break
                result["items"].append(parsed)
            if not result["items"]:
                result["items"].append(self.default_rule())
            return result
        return None

    def render(self, json: dict) -> str:
        pass
