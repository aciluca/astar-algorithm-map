"""Utility helpers for formatting values and rendering maps."""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import folium
import networkx as nx
import osmnx as ox


def create_route_map(
    coordinates: Sequence[Tuple[float, float]],
    *,
    graph: Optional[nx.MultiDiGraph] = None,
    start_name: str = "Start",
    end_name: str = "End",
    color: str = "blue",
) -> Optional[folium.Map]:
    """Create a folium map overlaying the route on top of the road network."""

    if not coordinates:
        return None

    if graph is not None:
        fmap = ox.plot_graph_folium(graph, weight=2, color="#777777", opacity=0.4)
    else:
        center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
        center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
        fmap = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    folium.PolyLine(coordinates, color=color, weight=5, opacity=0.9).add_to(fmap)

    folium.Marker(
        coordinates[0],
        popup=start_name,
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(fmap)

    folium.Marker(
        coordinates[-1],
        popup=end_name,
        icon=folium.Icon(color="red", icon="stop"),
    ).add_to(fmap)

    return fmap


def format_distance(meters: float) -> str:
    """Format a distance in metres using human-readable units."""

    if meters < 1000:
        return f"{meters:.0f} m"
    return f"{meters / 1000:.2f} km"


def format_time(seconds: float) -> str:
    """Format a duration in seconds using minutes and hours when appropriate."""

    if seconds < 60:
        return f"{seconds:.0f} sec"
    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f} min"
    hours = seconds / 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:.2f} hr {minutes:.0f} min"
