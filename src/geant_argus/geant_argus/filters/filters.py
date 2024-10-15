import dataclasses
import datetime
import functools
import itertools
import operator

from django.db.models import Q, QuerySet


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

    def to_sql(self, db_field: str, op: str, rule: dict):
        raise NotImplementedError


class TextOperator(Operator):
    template = "geant/filters/_filter_text_input.html"

    def initial_value(self):
        return {"value": ""}

    def parse_formdata(self, form_data: dict, prefix):
        return {"value": form_data.get(prefix + "val:str", "")[:100]}

    def to_sql(self, db_field: str, op: str, rule: dict):
        if op == "contains":
            return Q(**{f"{db_field}__icontains": rule["value"]})
        if op == "equals":
            return Q(**{f"{db_field}": rule["value"]})


class BooleanOperator(Operator):
    template = "geant/filters/_filter_boolean_input.html"

    def initial_value(self):
        return {"value": True}

    def parse_formdata(self, form_data: dict, prefix: str):
        raw = form_data.get(prefix + "val:bool", "true")
        return {"value": raw == "true"}

    def to_sql(self, db_field: str, op: str, rule: dict):
        if op != "is":
            return None

        # TODO: implement for acks
        return None


class DateTimeOperator(Operator):
    NORMALIZED_DATETIME = "%Y-%m-%dT%H:%M"
    template = "geant/filters/_filter_datetime_picker.html"

    def initial_value(self):
        return {"value": datetime.datetime.now().strftime(self.NORMALIZED_DATETIME)}

    def parse_formdata(self, form_data: dict, prefix: str):
        raw = form_data.get(prefix + "val:datetime", "")
        try:
            datetime.datetime.strptime(raw, self.NORMALIZED_DATETIME)
        except ValueError:
            raw = datetime.datetime.now().strftime(self.NORMALIZED_DATETIME)
        return {"value": raw}

    def to_sql(self, db_field: str, op: str, rule: dict):
        if op == "before_abs":
            return Q(**{f"{db_field}__lt": rule["value"]})
        if op == "after_abs":
            return Q(**{f"{db_field}__gt": rule["value"]})


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

    def to_sql(self, db_field: str, op: str, rule: dict):
        target_dt = datetime.datetime.now(tz=datetime.timezone.utc) - self.rule_to_timedelta(rule)
        if op == "before_rel":
            return Q(**{f"{db_field}__lt": target_dt})
        if op == "after_rel":
            return Q(**{f"{db_field}__gt": target_dt})

    def rule_to_timedelta(self, rule):
        amount = rule["value"]
        time_unit_raw = rule["unit"]

        return {
            "minutes": datetime.timedelta(minutes=amount),
            "hours": datetime.timedelta(hours=amount),
            "days": datetime.timedelta(days=amount),
            "weeks": datetime.timedelta(weeks=amount),
        }[time_unit_raw]


@dataclasses.dataclass
class FilterField:
    name: str
    display_name: str
    operators: list[Operator]
    db_fields: list[str]

    def __post_init__(self):
        assert self.db_fields, "db_fields must have at least one item"
        assert self.operators, "operators must have at least one item"
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
            return {
                "type": "rule",
                "field": self.name,
                "operator": op.name,
                **op.parse_formdata(form_data, prefix),
            }

        op = self.operators_by_name[op_str]
        return {
            "type": "rule",
            "field": self.name,
            "operator": op.name,
            **op.parse_formdata(form_data, prefix=prefix),
        }

    def to_sql(self, rule: dict):
        op_str: str = rule.get("operator")
        if (op := self.operators_by_name.get(op_str)) is None:
            return Q()

        return functools.reduce(
            operator.ior, (op.to_sql(f, op_str, rule) or Q() for f in self.db_fields)
        )


class ComplexFilter:
    version = "v1"

    def __init__(self, fields: list[FilterField]):
        self.fields = fields
        self.fields_by_name = {field.name: field for field in self.fields}

    def default_rule(self):
        field = self.fields[0]
        return field.default_rule()

    def default_group(self, operator="or", items=None):
        items = items or [self.default_rule()]
        return {"type": "group", "operator": operator, "items": items}

    def with_version(self, filter_dict: dict):
        return {"version": self.version, **filter_dict}

    def parse_form_data(self, form_data: dict) -> dict:
        return self.with_version(self._parse_formdata_helper(form_data, prefix=""))

    def _parse_formdata_helper(self, form_data: dict, prefix: str) -> dict:
        if try_field := form_data.get(prefix + "field"):
            if try_field in ("or", "and"):
                return self.default_group(operator=try_field)
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

    def filter_queryset(self, qs: QuerySet, filter_dict: dict) -> QuerySet:
        if filter_dict["version"] != "v1":
            raise ValueError("unsupported filter version")

        return qs.filter(self._parse_filter_item(filter_dict))

    def _parse_filter_item(self, item: dict):
        if item["type"] == "group":
            return self._parse_filter_group(item)
        if item["type"] == "rule":
            return self._parse_filter_rule(item)
        raise ValueError("invalid item type")

    def _parse_filter_group(self, group: dict):
        op = operator.ior if group["operator"] == "or" else operator.iand
        return functools.reduce(op, (self._parse_filter_item(i) for i in group["items"]))

    def _parse_filter_rule(self, rule: dict):
        field = self.fields_by_name[rule["field"]]
        return field.to_sql(rule)


FILTER_MODEL = ComplexFilter(
    fields=[
        FilterField(
            "description",
            "Description",
            operators=[
                TextOperator("contains"),
            ],
            db_fields=["description"],
        ),
        # Comment field not yet supported
        # FilterField(
        #     "comment",
        #     "Comment",
        #     operators=[
        #         TextOperator("contains"),
        #     ],
        # ),
        FilterField(
            "location",
            "Location",
            operators=[
                TextOperator("contains"),
            ],
            db_fields=["metadata__location"],
        ),
        FilterField(
            "sd_ack",
            "Ack (SD)",
            operators=[
                BooleanOperator("is"),
            ],
            db_fields=["acks"],
        ),
        FilterField(
            "noc_ack",
            "Ack (NOC)",
            operators=[
                BooleanOperator("is"),
            ],
            db_fields=["acks"],
        ),
        FilterField(
            "start_time",
            "Start Time",
            operators=[
                DateTimeOperator("after_abs", "earliest"),
                DateTimeOperator("before_abs", "latest"),
                TimeDeltaOperator("after_rel", "younger"),
                TimeDeltaOperator("before_rel", "older"),
            ],
            db_fields=["start_time"],
        ),
    ]
)
