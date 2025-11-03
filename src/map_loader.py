"""Utility helpers for downloading and working with OpenStreetMap graphs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import networkx as nx
import osmnx as ox

DEFAULT_MAX_SPEED_KPH = 130.0


@dataclass(frozen=True)
class PathMetrics:
    """Aggregate statistics about a path in the road network."""

    distance_m: float
    travel_time_s: float
    edge_count: int

    @property
    def distance_km(self) -> float:
        """Return the path length in kilometres."""

        return self.distance_m / 1000.0

    @property
    def travel_time_min(self) -> float:
        """Return the travel time in minutes."""

        return self.travel_time_s / 60.0


class MapLoader:
    """Load and manage OpenStreetMap road networks using OSMnx."""

    def __init__(self) -> None:
        self.graph: Optional[nx.MultiDiGraph] = None
        self.place_name: Optional[str] = None
        self._max_speed_m_s: float = DEFAULT_MAX_SPEED_KPH / 3.6

    def load_map(
        self,
        place_name: Optional[str] = None,
        *,
        point: Optional[Tuple[float, float]] = None,
        dist: int = 1000,
        dist_type: str = "bbox",
        network_type: str = "drive",
        simplify: bool = True,
        retain_all: bool = False,
        custom_filter: Optional[str] = None,
    ) -> nx.MultiDiGraph:
        """Download a routable street network and add travel-time metadata."""

        if place_name is None and point is None:
            raise ValueError("Either 'place_name' or 'point' must be provided")

        try:
            if point is not None:
                self.place_name = place_name or f"Point @ {point[0]:.5f}, {point[1]:.5f}"
                self.graph = ox.graph_from_point(
                    point,
                    dist=dist,
                    dist_type=dist_type,
                    network_type=network_type,
                    simplify=simplify,
                    retain_all=retain_all,
                    custom_filter=custom_filter,
                )
            else:
                assert place_name is not None
                self.place_name = place_name
                self.graph = ox.graph_from_place(
                    place_name,
                    network_type=network_type,
                    simplify=simplify,
                    retain_all=retain_all,
                    custom_filter=custom_filter,
                )

            self.graph = ox.add_edge_speeds(self.graph)
            self.graph = ox.add_edge_travel_times(self.graph)
            self._max_speed_m_s = self._compute_max_speed(self.graph)
            return self.graph
        except Exception as exc:  # pragma: no cover - transparent error reporting
            raise RuntimeError(f"Error loading map: {exc}") from exc

    def get_nearest_node(self, point: Tuple[float, float]) -> int:
        """Return the node id closest to the provided (lat, lon) coordinates."""

        self._ensure_graph_loaded()
        assert self.graph is not None
        return ox.distance.nearest_nodes(self.graph, point[1], point[0])  # lon, lat

    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """Return a node's coordinates as ``(lat, lon)``."""

        self._ensure_graph_loaded()
        assert self.graph is not None
        node = self.graph.nodes[node_id]
        return node["y"], node["x"]

    def path_to_coordinates(self, path: Sequence[int]) -> List[Tuple[float, float]]:
        """Convert a sequence of node ids into geographic coordinates."""

        self._ensure_graph_loaded()
        return [self.get_node_coordinates(node_id) for node_id in path]

    def calculate_path_metrics(self, path: Sequence[int]) -> PathMetrics:
        """Return aggregated metrics (length and travel time) for ``path``."""

        self._ensure_graph_loaded()
        assert self.graph is not None

        total_length = 0.0
        total_time = 0.0
        edge_count = 0

        for edge_data in self._iter_edge_attributes(path):
            length = float(edge_data.get("length", 0.0))
            travel_time_attr = edge_data.get("travel_time")
            if travel_time_attr is not None:
                travel_time = float(travel_time_attr)
            else:
                travel_time = self._length_to_travel_time(length, edge_data)

            total_length += length
            total_time += travel_time
            edge_count += 1

        return PathMetrics(distance_m=total_length, travel_time_s=total_time, edge_count=edge_count)

    def get_graph_info(self) -> Dict[str, object]:
        """Expose basic information about the currently loaded graph."""

        if self.graph is None:
            return {}
        return {
            "num_nodes": len(self.graph.nodes),
            "num_edges": len(self.graph.edges),
            "place_name": self.place_name,
        }

    def _ensure_graph_loaded(self) -> None:
        if self.graph is None:
            raise RuntimeError("Graph not loaded. Call 'load_map' first.")

    def _iter_edge_attributes(self, path: Sequence[int]) -> Iterable[Mapping[str, object]]:
        assert self.graph is not None

        for src, dst in zip(path, path[1:]):
            edge_bundle = self.graph.get_edge_data(src, dst) or {}
            if not edge_bundle:
                continue

            best_edge = min(
                edge_bundle.values(),
                key=lambda data: data.get("travel_time", data.get("length", float("inf"))),
            )
            yield best_edge

    def _compute_max_speed(self, graph: nx.MultiDiGraph) -> float:
        max_speed_kph = 0.0
        for _, _, data in graph.edges(data=True):
            speed = self._edge_speed_kph(data)
            if speed is not None and speed > max_speed_kph:
                max_speed_kph = speed
        if max_speed_kph <= 0:
            max_speed_kph = DEFAULT_MAX_SPEED_KPH
        return max_speed_kph / 3.6

    def _length_to_travel_time(self, length: float, edge_data: Mapping[str, object]) -> float:
        speed = self._edge_speed_m_s(edge_data) or self._max_speed_m_s
        if speed <= 0:
            return 0.0
        return length / speed

    def _edge_speed_m_s(self, data: Mapping[str, object]) -> Optional[float]:
        speed_kph = self._edge_speed_kph(data)
        return speed_kph / 3.6 if speed_kph is not None else None

    def _edge_speed_kph(self, data: Mapping[str, object]) -> Optional[float]:
        speed = data.get("speed_kph") or data.get("maxspeed")
        if isinstance(speed, (list, tuple)) and speed:
            speed = speed[0]
        if isinstance(speed, str):
            if ";" in speed:
                speed = speed.split(";")[0]
            speed = speed.replace("km/h", "").replace("kph", "").strip()
            if "mph" in speed.lower():
                value = self._coerce_float(speed.lower().replace("mph", ""))
                return value * 1.60934 if value is not None else None
            return self._coerce_float(speed)
        return self._coerce_float(speed)

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
