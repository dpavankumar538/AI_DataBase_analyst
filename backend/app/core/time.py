from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC time as a naive datetime (tzinfo stripped).

    Naive datetimes are used throughout to match the MySQL DateTime column
    type which has no timezone awareness. All stored values are implicitly UTC.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
