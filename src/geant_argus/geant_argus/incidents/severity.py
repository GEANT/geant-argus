import enum


class StrComparableEnumMeta(enum.EnumMeta):
    def __contains__(cls, member):
        if isinstance(member, str):
            return member in cls.__members__
        return super().__contains__(member)


class IncidentSeverity(enum.IntEnum, metaclass=StrComparableEnumMeta):
    """Reverse from dashboard.correlation.enums.AlarmSeverity"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5
