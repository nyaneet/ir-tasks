"""
Helper functions for interval splitting
"""
from typing import List, Tuple


def get_subintervals(left: int, right: int,
                     n_intervals: int) -> Tuple[List[int], List[int]]:
    """
    Split the original interval into subintervals.

    Args:
        left: Left bound of the original interval.
        right: Right bound of the original interval.
        n_intervals: Number of subintervals.

    Returns:
        Two lists:
        - List of left bounds of intervals;
        - List of right bounds of intervals;
    """
    left_bounds = []
    right_bounds = []

    k, m = divmod(right - left, n_intervals)
    for i in range(n_intervals):
        left_bounds.append(i * k + min(i, m))
        right_bounds.append((i + 1) * k + min(i + 1, m))

    return left_bounds, right_bounds
