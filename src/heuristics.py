"""Heuristic helpers for the routing algorithms."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Tuple

DEFAULT_MAX_SPEED_KPH = 130.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance between two geographic coordinates."""

    radius = 6_371_000  # metres

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius * c


class Heuristic(ABC):
    """Abstract base class for heuristic distance estimators."""

    @abstractmethod
    def calculate(self, node1: Tuple[float, float], node2: Tuple[float, float]) -> float:
        """Return the estimated cost between two nodes."""


class EuclideanHeuristic(Heuristic):
    """Great-circle distance between two coordinates."""

    def calculate(self, node1: Tuple[float, float], node2: Tuple[float, float]) -> float:
        lat1, lon1 = node1
        lat2, lon2 = node2
        return haversine_distance(lat1, lon1, lat2, lon2)


class TravelTimeHeuristic(Heuristic):
    """Estimate the minimum travel time assuming an optimistic top speed."""

    def __init__(self, max_speed_m_s: float = DEFAULT_MAX_SPEED_KPH / 3.6) -> None:
        if max_speed_m_s <= 0:
            raise ValueError("max_speed_m_s must be positive")
        self.max_speed_m_s = float(max_speed_m_s)

    def calculate(self, node1: Tuple[float, float], node2: Tuple[float, float]) -> float:
        lat1, lon1 = node1
        lat2, lon2 = node2
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        return distance / self.max_speed_m_s


class ManhattanHeuristic(Heuristic):
    """Orthogonal approximation based on the Haversine metric."""

    def calculate(self, node1: Tuple[float, float], node2: Tuple[float, float]) -> float:
        lat1, lon1 = node1
        lat2, lon2 = node2

        lat_dist = haversine_distance(lat1, lon1, lat2, lon1)
        lon_dist = haversine_distance(lat1, lon1, lat1, lon2)
        return lat_dist + lon_dist


class ZeroHeuristic(Heuristic):
    """Trivial heuristic that disables the A* speed-up (equivalent to Dijkstra)."""

    def calculate(self, node1: Tuple[float, float], node2: Tuple[float, float]) -> float:
        return 0.0
