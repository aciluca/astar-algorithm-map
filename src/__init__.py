"""
A* Pathfinding Package
"""

# Export from heuristics
from .heuristics import (
    Heuristic,
    EuclideanHeuristic,
    ManhattanHeuristic, 
    ZeroHeuristic,
    haversine_distance  # Only if you choose Option 2
)

# Export other modules
from .map_loader import MapLoader
from .graph import RoadGraph
from .astar import AStar, Dijkstra
from .utils import create_route_map, format_distance, format_time

__all__ = [
    'Heuristic',
    'EuclideanHeuristic',
    'ManhattanHeuristic',
    'ZeroHeuristic',
    'haversine_distance',  # Only if you choose Option 2
    'MapLoader',
    'RoadGraph', 
    'AStar',
    'Dijkstra',
    'create_route_map',
    'format_distance',
    'format_time'
]

__version__ = "1.0.0"