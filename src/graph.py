"""Utilities for working with road-network graphs."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Mapping, Tuple

import networkx as nx


class RoadGraph:
    """Light-weight wrapper to expose graph operations needed by A*."""

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

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

    def _iter_outgoing_edges(self, node: int) -> Iterator[Tuple[int, Iterable[Mapping[str, object]]]]:
        try:
            neighbors = self.graph.succ[node]
        except KeyError:
            return iter(())
        return ((neighbor, key_dict.values()) for neighbor, key_dict in neighbors.items())

    @staticmethod
    def _edge_cost(edges: Iterable[Mapping[str, object]]) -> float | None:
        best_cost: float | None = None
        for data in edges:
            weight = data.get("travel_time")
            if weight is None:
                weight = data.get("length")
            if weight is None:
                continue
            weight = float(weight)
            if best_cost is None or weight < best_cost:
                best_cost = weight
        return best_cost
