import dataclasses
import datetime
import functools
import itertools
import operator
from typing import Optional, Type, Union

from django.db.models import JSONField, Q, QuerySet, Value


@dataclasses.dataclass
class DBField:
    name: str
    type: Union[Type[str], Type[bool]] = str
    is_json: bool = False

    def __str__(self):
        return self.name


class Operator:
    template: str

    def __init__(self, name: str, display_name: str = None):
        self.name = name
        self.display_name = display_name if display_name is not None else name

    @staticmethod
    def is_json_null(field: DBField):
        return Q(**{str(field): Value(None, JSONField())}) if field.is_json else Q()

    def initial_value(self):
        raise NotImplementedError

    def parse_formdata(self, form_data: dict, prefix: str):
        raise NotImplementedError

    def to_sql(self, db_field: DBField, op: str, rule: dict):
        raise NotImplementedError


class TextOperator(Operator):
    template = "geant/filters/_filter_text_input.html"

    def initial_value(self):
        return {"value": ""}

    def parse_formdata(self, form_data: dict, prefix):
        return {"value": form_data.get(prefix + "val:str", "")[:100]}

    def to_sql(self, db_field: DBField, op: str, rule: dict):
        not_null = ~self.is_json_null(db_field)

        if op == "contains":
            return not_null & Q(**{f"{db_field}__icontains": rule["value"]})
        if op == "equals":
            return not_null & Q(**{str(db_field): rule["value"]})


class BooleanOperator(Operator):
    template = "geant/filters/_filter_boolean_input.html"

    def initial_value(self):
        return {"value": True}

    def parse_formdata(self, form_data: dict, prefix: str):
        raw = form_data.get(prefix + "val:bool", "false")
        return {"value": raw == "true"}

    def to_sql(self, db_field: DBField, op: str, rule: dict):
        not_null = ~self.is_json_null(db_field)

        if op != "is":
            return None
        return not_null & Q(**{str(db_field): rule["value"]})


class ExistsOperator(Operator):
    template = "geant/filters/_filter_exists.html"

    def initial_value(self):
        return {"value": True}

    def parse_formdata(self, form_data: dict, prefix: str):
        return self.initial_value()

    def to_sql(self, db_field: DBField, op: str, rule: dict):
        if op != "exists":
            return None
        is_null = self.is_json_null(db_field)
        if db_field.type == str:
            return ~(is_null | Q(**{str(db_field): ""}))
        else:
            return ~(is_null | Q(**{str(db_field): False}))


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

    def to_sql(self, db_field: DBField, op: str, rule: dict):
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

    def to_sql(self, db_field: DBField, op: str, rule: dict):
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
    db_fields: list[Union[str, DBField]]
    invertable: bool = False
    row_template: str = "geant/filters/_filter_rule_row.html"

    def __post_init__(self):
        assert self.db_fields, "db_fields must have at least one item"
        assert self.operators, "operators must have at least one item"
        self.operators_by_name = {op.name: op for op in self.operators}

    @staticmethod
    def as_dbfield(field: Union[str, DBField]):
        if isinstance(field, DBField):
            return field
        return DBField(field)

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
        invert = {"invert": True} if (self.invertable and form_data.get(prefix + "invert")) else {}
        return {
            "type": "rule",
            "field": self.name,
            "operator": op.name,
            **invert,
            **op.parse_formdata(form_data, prefix=prefix),
        }

    def to_sql(self, rule: dict):
        op_str: str = rule.get("operator")
        if (op := self.operators_by_name.get(op_str)) is None:
            return Q()

        return functools.reduce(
            operator.ior,
            (op.to_sql(self.as_dbfield(f), op_str, rule) or Q() for f in self.db_fields),
        )


class ComplexFilter:
    version = "v1"
    VALID_GROUP_OPERATORS = ("or", "and", "none")

    def __init__(self, fields: list[FilterField]):
        self.fields = fields
        self.fields_by_name = {field.name: field for field in self.fields}

    def default_rule(self):
        field = self.fields[0]
        return field.default_rule()

    def default_group(self, operator=VALID_GROUP_OPERATORS[0], items=None):
        items = items or [self.default_rule()]
        return {"type": "group", "operator": operator, "items": items}

    def parse_form_data(self, form_data: dict) -> Optional[dict]:
        result = self._parse_formdata_helper(form_data, prefix="")
        if not result:
            return None
        return self.with_version(result)

    def _parse_formdata_helper(self, form_data: dict, prefix: str) -> Optional[dict]:
        if try_field := form_data.get(prefix + "field"):
            if try_field in self.VALID_GROUP_OPERATORS:
                return self.default_group(operator=try_field)
            field = self.fields_by_name.get(try_field, self.fields[0])
            return field.parse_form_data(form_data, prefix=prefix)

        if (try_field := form_data.get(prefix + "op")) is not None:
            if try_field not in self.VALID_GROUP_OPERATORS:
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

    # --------- Begin Filter to Queryset Methods -------------

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
        op = group["operator"]
        # "none" operator is first taken as "or" and then inverted resulting in a 'not any'
        # operation
        op_func = operator.iand if group["operator"] == "and" else operator.ior
        result = functools.reduce(op_func, (self._parse_filter_item(i) for i in group["items"]))
        if op == "none":
            result = ~result
        return result

    def _parse_filter_rule(self, rule: dict):
        field = self.fields_by_name[rule["field"]]
        result = field.to_sql(rule)
        if rule.get("invert"):
            result = ~result
        return result

    # --------- End Filter to Queryset Methods -------------

    def upgrade_simple_filter(self, filter_dict: dict, operator="or"):
        if filter_dict["type"] == "group":
            return filter_dict
        copy = filter_dict.copy()
        copy.pop("version", None)
        return self.default_group(operator=operator, items=[copy])

    @classmethod
    def with_version(cls, filter_dict: dict):
        return {"version": cls.version, **filter_dict}


def filter_to_text(filter_dict):
    def _dispatch(filter_dict):
        if filter_dict["type"] == "rule":
            return _handle_rule(filter_dict)
        if filter_dict["type"] == "group":
            return _handle_group(filter_dict)
        return ""

    def _handle_rule(filter_dict):
        field, op = filter_dict["field"].upper(), filter_dict["operator"]
        invert = "NOT " if filter_dict.get("invert") else ""

        match op:
            case "exists":
                return f"{field} {invert}{op}"
            case "before_abs":
                return f"{field} {invert}before {filter_dict['value']}"
            case "after_abs":
                return f"{field} {invert}after {filter_dict['value']}"
            case "before_rel":
                return f"{field} {invert}before {filter_dict['value']} {filter_dict['unit']} ago"
            case "after_rel":
                return f"{field} {invert}after {filter_dict['value']} {filter_dict['unit']} ago"
            case "is":
                return f"{field} {invert}{op} {str(filter_dict['value']).upper()}"
            case _:
                return f"{field} {invert}{op} '{filter_dict['value']}'"
        return

    def _handle_group(filter_dict):
        op = filter_dict["operator"].upper()
        item_texts = [_dispatch(item) for item in filter_dict["items"]]

        invert = ""
        if op == "NONE":
            op = "OR"
            invert = "NOT "

        if len(item_texts) == 0:
            return ""
        if not invert and len(item_texts) == 1:
            return item_texts[0]
        return f"{invert}({f' {op} '.join(item_texts)})"

    return _dispatch(filter_dict)


FILTER_MODEL = ComplexFilter(
    fields=[
        FilterField(
            "description",
            "Description",
            operators=[
                TextOperator("contains"),
            ],
            db_fields=["description"],
            invertable=True,
        ),
        FilterField(
            "comment",
            "Comment",
            operators=[
                TextOperator("contains"),
                ExistsOperator("exists"),
            ],
            db_fields=[DBField("metadata__comment", is_json=True)],
            invertable=True,
        ),
        FilterField(
            "location",
            "Location",
            operators=[
                TextOperator("contains"),
            ],
            db_fields=[DBField("metadata__location", is_json=True)],
            invertable=True,
        ),
        FilterField(
            "equipment",
            "Equipment",
            operators=[
                TextOperator("contains"),
            ],
            db_fields=[DBField("metadata__equipment", is_json=True)],
            invertable=True,
        ),
        FilterField(
            "ticket_ref",
            "Ticket Ref",
            operators=[
                TextOperator("contains"),
            ],
            db_fields=[DBField("metadata__ticket_ref", is_json=True)],
            invertable=True,
        ),
        FilterField(
            "ack",
            "Ack",
            operators=[
                ExistsOperator("exists"),
            ],
            db_fields=[DBField("ack", type=bool)],
            invertable=True,
        ),
        FilterField(
            "short_lived",
            "Short Lived",
            operators=[
                BooleanOperator("is"),
            ],
            db_fields=[DBField("metadata__short_lived", type=bool, is_json=True)],
            row_template="geant/filters/_filter_boolean_row.html",
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
