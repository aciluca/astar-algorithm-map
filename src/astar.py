"""Implementations of the A* and Dijkstra pathfinding algorithms."""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

from .graph import RoadGraph
from .heuristics import Heuristic


class AStar:
    """A* pathfinding algorithm operating on :class:`RoadGraph`."""

    def __init__(self, graph: RoadGraph, heuristic: Optional[Heuristic] = None):
        self.graph = graph
        self.heuristic = heuristic if heuristic else graph.default_heuristic()

    def find_path(self, start: int, goal: int) -> Tuple[List[int], float]:
        """Find the shortest path from ``start`` to ``goal`` using A*."""

        open_set: List[Tuple[float, int]] = []
        heapq.heappush(open_set, (0.0, start))

        came_from: Dict[int, Optional[int]] = {start: None}
        g_score: Dict[int, float] = {start: 0.0}
        f_score: Dict[int, float] = {start: self._heuristic_cost(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current), g_score[goal]

            for neighbor, weight in self.graph.get_neighbors(current):
                tentative_g = g_score[current] + weight

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic_cost(neighbor, goal)

                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return [], float("inf")

    def _heuristic_cost(self, node1: int, node2: int) -> float:
        coord1 = self.graph.get_node_coordinates(node1)
        coord2 = self.graph.get_node_coordinates(node2)
        return self.heuristic.calculate(coord1, coord2)

    def _reconstruct_path(self, came_from: Dict[int, Optional[int]], current: int) -> List[int]:
        path = [current]
        while current in came_from and came_from[current] is not None:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))


class Dijkstra:
    """Dijkstra's algorithm operating on :class:`RoadGraph`."""

    def __init__(self, graph: RoadGraph):
        self.graph = graph

    def find_path(self, start: int, goal: int) -> Tuple[List[int], float]:
        distance = {node: float("inf") for node in self.graph.get_all_nodes()}
        distance[start] = 0.0
        previous = {node: None for node in self.graph.get_all_nodes()}

        unvisited = set(self.graph.get_all_nodes())

        while unvisited:
            current = min(unvisited, key=lambda node: distance[node])
            unvisited.remove(current)

            if current == goal:
                break

            if distance[current] == float("inf"):
                break

            for neighbor, weight in self.graph.get_neighbors(current):
                new_distance = distance[current] + weight
                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    previous[neighbor] = current
        return self._reconstruct_path(previous, goal), distance[goal]

    def _reconstruct_path(self, previous: Dict[int, Optional[int]], goal: int) -> List[int]:
        path: List[int] = []
        current: Optional[int] = goal
        while current is not None:
            path.append(current)
            current = previous[current]
        return list(reversed(path))
