"""
Compatibility helpers shared across the sensor app.
"""
from datetime import datetime, timedelta

SQLITE_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def cutoff_timestamp(hours: int) -> str:
    """Return a SQLite-friendly cutoff timestamp string."""
    return (datetime.now() - timedelta(hours=hours)).strftime(SQLITE_TIMESTAMP_FORMAT)


def format_timestamp(value) -> str:
    """Format timestamps from SQLite for display, handling multiple inputs."""
    parsed = parse_timestamp(value)
    if parsed is None:
        return "" if value is None else str(value)
    return parsed.strftime(DISPLAY_TIMESTAMP_FORMAT)


def parse_timestamp(value):
    """Parse SQLite or ISO timestamps into a datetime, if possible."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(" ", "T", 1) if "T" not in text and " " in text else text
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d",
        "%d/%m/%y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def rerun_streamlit():
    """Trigger a Streamlit rerun using the best API available."""
    import streamlit as st

    rerun = getattr(st, "rerun", None)
    if callable(rerun):
        rerun()
        return

    experimental_rerun = getattr(st, "experimental_rerun", None)
    if callable(experimental_rerun):
        experimental_rerun()

