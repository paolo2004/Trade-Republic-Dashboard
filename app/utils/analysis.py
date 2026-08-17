import pandas as pd


def format_number(value, decimals=2):
    """Format numbers safely."""

    if value is None or pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_large_number(value):
    """Format large numbers like market cap."""

    if value is None or pd.isna(value):
        return "N/A"

    try:
        value = float(value)

        if value >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f} T"

        elif value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f} B"

        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f} M"

        else:
            return f"{value:,.0f}"

    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value):
    """Convert decimal percentage to readable percentage."""

    if value is None or pd.isna(value):
        return "N/A"

    try:
        return f"{float(value) * 100:.2f}%"
    except (ValueError, TypeError):
        return "N/A"
