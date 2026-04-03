import math
from decimal import Decimal


def shoelace_area_acres(coordinates):
    """
    Calculate polygon area in acres from a list of (lat, lon) tuples
    using the Shoelace formula with equirectangular projection to metres.
    Used as a fallback when PostGIS is unavailable (e.g. PWA offline).
    """
    n = len(coordinates)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        lat_i, lon_i = coordinates[i]
        lat_j, lon_j = coordinates[j]

        # Approximate metres using equirectangular projection
        xi = lon_i * 111320 * math.cos(math.radians(lat_i))
        yi = lat_i * 110540
        xj = lon_j * 111320 * math.cos(math.radians(lat_j))
        yj = lat_j * 110540

        area += xi * yj - xj * yi

    area_m2 = abs(area) / 2
    return round(area_m2 / 4046.86, 3)  # 1 acre = 4046.86 m²


def format_ugx(amount):
    """Format a number as Ugandan Shillings."""
    if amount is None:
        return 'UGX 0'
    return f"UGX {int(amount):,}"


def percentage_change(before, after):
    """Calculate percentage change between two values."""
    if before == 0:
        return 100.0 if after > 0 else 0.0
    return round(float((after - before) / before * 100), 1)


def safe_divide(numerator, denominator, default=Decimal('0')):
    """Division that returns default instead of raising ZeroDivisionError."""
    if denominator == 0:
        return default
    return numerator / denominator
