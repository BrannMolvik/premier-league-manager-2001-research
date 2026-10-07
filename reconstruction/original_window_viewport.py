"""Modern window-fit adapter; original content stays in 800x600 coordinates."""
from math import gcd


def window_fit_scale(width: int, height: int) -> tuple[int, int]:
    """Largest bounded rational fit, including windows smaller than native size.

    Integer arithmetic ensures the rounded-up raster never exceeds the client.
    This is a compatibility viewport, not original game/presentation timing.
    """
    if type(width) is not int or type(height) is not int or width < 50 or height < 38:
        raise ValueError('Game client is too small for a bounded viewport')
    best_num, best_den = 0, 1
    for denominator in range(1, 17):
        numerator = min(width * denominator // 800, height * denominator // 600)
        if numerator * best_den > best_num * denominator:
            best_num, best_den = numerator, denominator
    divisor = gcd(best_num, best_den)
    return best_num // divisor, best_den // divisor
