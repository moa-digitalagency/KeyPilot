from datetime import datetime, timezone

def format_date(date_obj):
    """Formats a datetime object to YYYY-MM-DD string."""
    if not date_obj:
        return None
    return date_obj.strftime("%Y-%m-%d")

def calculate_remaining_days(expiration_date):
    """Calculates remaining days until expiration from now (UTC)."""
    if not expiration_date:
        return 0

    # Ensure expiration_date is timezone-aware if it isn't already
    if expiration_date.tzinfo is None:
        expiration_date = expiration_date.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delta = expiration_date - now
    return max(0, delta.days)
