from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_utc_naive(value: datetime) -> datetime:
    return to_utc_datetime(value).replace(tzinfo=None)
