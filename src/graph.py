"""Utilities for working with road-network graphs."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Mapping, Optional, Tuple

import networkx as nx

from .heuristics import EuclideanHeuristic, Heuristic, TravelTimeHeuristic

DEFAULT_MAX_SPEED_KPH = 130.0

class RoadGraph:
    """Light-weight wrapper to expose graph operations needed by A*."""

    def __init__(self, graph: nx.MultiDiGraph, *, weight_attr: str = "travel_time"):
        self.graph = graph
        self.weight_attr = weight_attr
        self._max_speed_m_s = self._compute_max_speed()

    def get_neighbors(self, node: int) -> List[Tuple[int, float]]:
        """Return the neighbouring nodes and the associated travel costs."""

        neighbors: List[Tuple[int, float]] = []
        for neighbor, edges in self._iter_outgoing_edges(node):
            cost = self._edge_cost(edges)
            if cost is None:
                continue
            neighbors.append((neighbor, cost))
        return neighbors

    def get_node_coordinates(self, node: int) -> Tuple[float, float]:
        """Return a node's latitude and longitude."""

        node_data = self.graph.nodes[node]
        return float(node_data["y"]), float(node_data["x"])

    def get_edge_weight(self, node1: int, node2: int) -> float:
        """Return the minimum travel time between two nodes if an edge exists."""

        edges = self.graph.get_edge_data(node1, node2) or {}
        cost = self._edge_cost(edges.values())
        return cost if cost is not None else float("inf")

    def get_all_nodes(self) -> List[int]:
        """Return a list of all node ids present in the graph."""

        return list(self.graph.nodes)

    def default_heuristic(self) -> Heuristic:
        """Return an admissible heuristic compatible with the weight attribute."""

        if self.weight_attr == "travel_time":
            return TravelTimeHeuristic(self._max_speed_m_s)
        return EuclideanHeuristic()

    @property
    def max_speed_m_s(self) -> float:
        return self._max_speed_m_s

    def _iter_outgoing_edges(self, node: int) -> Iterator[Tuple[int, Iterable[Mapping[str, object]]]]:
        try:
            neighbors = self.graph.succ[node]
        except KeyError:
            return iter(())
        return ((neighbor, key_dict.values()) for neighbor, key_dict in neighbors.items())

    def _edge_cost(self, edges: Iterable[Mapping[str, object]]) -> Optional[float]:
        best_cost: Optional[float] = None
        for data in edges:
            weight = data.get(self.weight_attr)
            if weight is not None:
                weight = self._coerce_float(weight)
            if weight is None:
                weight = self._fallback_weight(data)
            if weight is None:
                continue
            if best_cost is None or weight < best_cost:
                best_cost = weight
        return best_cost

    def _fallback_weight(self, data: Mapping[str, object]) -> Optional[float]:
        length = self._coerce_float(data.get("length"))
        if length is None:
            return None
        if self.weight_attr == "travel_time":
            speed = self._edge_speed_m_s(data) or self._max_speed_m_s
            if speed <= 0:
                return None
            return length / speed
        return length

    def _compute_max_speed(self) -> float:
        max_speed_kph = 0.0
        for _, _, data in self.graph.edges(data=True):
            speed = self._edge_speed_kph(data)
            if speed is not None and speed > max_speed_kph:
                max_speed_kph = speed
        if max_speed_kph <= 0:
            max_speed_kph = DEFAULT_MAX_SPEED_KPH
        return max_speed_kph / 3.6

    def _edge_speed_m_s(self, data: Mapping[str, object]) -> Optional[float]:
        speed_kph = self._edge_speed_kph(data)
        return speed_kph / 3.6 if speed_kph is not None else None

    @staticmethod
    def _edge_speed_kph(data: Mapping[str, object]) -> Optional[float]:
        speed = data.get("speed_kph") or data.get("maxspeed")
        if isinstance(speed, (list, tuple)) and speed:
            speed = speed[0]
        if isinstance(speed, str):
            if ";" in speed:
                speed = speed.split(";")[0]
            speed = speed.replace("km/h", "").replace("kph", "").strip()
            if "mph" in speed.lower():
                value = RoadGraph._coerce_float(speed.lower().replace("mph", ""))
                return value * 1.60934 if value is not None else None
            return RoadGraph._coerce_float(speed)
        return RoadGraph._coerce_float(speed)

    @staticmethod
    def _coerce_float(value: object) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            try:
                return float(value)
            except ValueError:
                return None
        return None
