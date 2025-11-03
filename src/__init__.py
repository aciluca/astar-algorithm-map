"""Public API for the A* pathfinding utilities."""

from .astar import AStar, Dijkstra
from .graph import RoadGraph
from .heuristics import (
    EuclideanHeuristic,
    Heuristic,
    ManhattanHeuristic,
    ZeroHeuristic,
    haversine_distance,
)
from .map_loader import MapLoader, PathMetrics
from .utils import create_route_map, format_distance, format_time

__all__ = [
    "Heuristic",
    "EuclideanHeuristic",
    "ManhattanHeuristic",
    "ZeroHeuristic",
    "haversine_distance",
    "PathMetrics",
    "MapLoader",
    "RoadGraph",
    "AStar",
    "Dijkstra",
    "create_route_map",
    "format_distance",
    "format_time",
]

__version__ = "1.1.0"
