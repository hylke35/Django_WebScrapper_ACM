import enum


class CompanyStatus(enum.Enum):
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    NAME_CHANGE = "NAME_CHANGE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
    