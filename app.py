"""Streamlit interface for exploring A* routing on OpenStreetMap data."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Tuple

import osmnx as ox
import streamlit as st
from streamlit.components.v1 import html

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import (  # noqa: E402  # isort:skip
    AStar,
    MapLoader,
    RoadGraph,
    create_route_map,
    format_distance,
    format_time,
)


NETWORK_TYPES: Dict[str, str] = {
    "drive": "Drive (cars, default)",
    "walk": "Walk (pedestrian network)",
    "bike": "Bike",
    "drive_service": "Drive service (local service roads)",
}

WEIGHTING_LABELS: Dict[str, str] = {
    "travel_time": "Fastest route (travel time)",
    "length": "Shortest route (distance)",
}


@st.cache_resource(show_spinner=False)
def load_map_loader(
    place: str,
    network_type: str,
    simplify: bool,
    retain_all: bool,
) -> MapLoader:
    """Download (or retrieve from cache) an OpenStreetMap graph for ``place``."""

    loader = MapLoader()
    loader.load_map(
        place_name=place,
        network_type=network_type,
        simplify=simplify,
        retain_all=retain_all,
    )
    return loader


@st.cache_data(show_spinner=False)
def geocode(query: str) -> Tuple[float, float]:
    """Return latitude/longitude coordinates for a free-form query."""

    lat, lon = ox.geocode(query)
    return float(lat), float(lon)


def resolve_coordinates(
    mode: str,
    start_value: Tuple[float, float] | str,
    end_value: Tuple[float, float] | str,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Convert address or coordinate inputs into ``(lat, lon)`` tuples."""

    if mode == "Addresses":
        assert isinstance(start_value, str) and isinstance(end_value, str)
        start_coords = geocode(start_value)
        end_coords = geocode(end_value)
    else:
        assert isinstance(start_value, tuple) and isinstance(end_value, tuple)
        start_coords = start_value
        end_coords = end_value
    return start_coords, end_coords


def format_primary_cost(weight_attr: str, cost: float) -> str:
    if weight_attr == "travel_time":
        return format_time(cost)
    return format_distance(cost)


def main() -> None:
    st.set_page_config(
        page_title="A* Pathfinding on OpenStreetMap",
        page_icon="⭐",
        layout="wide",
    )

    st.title("A* Pathfinding on OpenStreetMap")
    st.write(
        "Explore the A* search algorithm on real road networks fetched from "
        "OpenStreetMap with [OSMnx](https://osmnx.readthedocs.io/). Choose an "
        "area, define start and end points, and compare the fastest versus the "
        "shortest path through the network."
    )

    with st.sidebar:
        st.header("Map options")
        place = st.text_input("Area to load", value="Rome, Italy")
        network_key = st.selectbox(
            "Network type",
            options=list(NETWORK_TYPES.keys()),
            format_func=lambda key: NETWORK_TYPES[key],
        )
        weight_attr = st.selectbox(
            "Cost metric",
            options=list(WEIGHTING_LABELS.keys()),
            format_func=lambda key: WEIGHTING_LABELS[key],
        )
        include_geometry = st.checkbox(
            "Follow curved street geometries", value=True, help="Use the geometry of each road segment so the polyline follows the actual street shape."
        )
        simplify = st.checkbox(
            "Simplify network", value=True, help="Let OSMnx merge nodes that form straight lines for cleaner graphs."
        )
        retain_all = st.checkbox(
            "Retain disconnected components", value=False, help="Keep isolated subgraphs instead of only the largest connected component."
        )
        color = st.color_picker("Route colour", value="#1d6be3")
        compute_route = st.button("Calculate route", type="primary")

    st.subheader("Waypoints")
    input_mode = st.radio(
        "Select how to provide the start and end points",
        options=["Addresses", "Coordinates"],
        horizontal=True,
    )

    if input_mode == "Addresses":
        start_address = st.text_input(
            "Start address",
            value="Piazza Navona, Rome",
            help="Use any address or landmark supported by OpenStreetMap's geocoder.",
        )
        end_address = st.text_input(
            "Destination address",
            value="Colosseum, Rome",
        )
        start_input: Tuple[float, float] | str = start_address
        end_input: Tuple[float, float] | str = end_address
    else:
        st.write("Enter latitude and longitude in decimal degrees (WGS84).")
        col1, col2 = st.columns(2)
        with col1:
            start_lat = st.number_input("Start latitude", value=41.899163, format="%.6f")
            start_lon = st.number_input("Start longitude", value=12.473075, format="%.6f")
        with col2:
            end_lat = st.number_input("Destination latitude", value=41.890210, format="%.6f")
            end_lon = st.number_input("Destination longitude", value=12.492231, format="%.6f")
        start_input = (float(start_lat), float(start_lon))
        end_input = (float(end_lat), float(end_lon))

    if compute_route:
        if not place.strip():
            st.error("Please provide an area to download from OpenStreetMap.")
            st.stop()

        try:
            with st.spinner("Loading OpenStreetMap data..."):
                loader = load_map_loader(place.strip(), network_key, simplify, retain_all)
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()

        try:
            start_coords, end_coords = resolve_coordinates(input_mode, start_input, end_input)
        except Exception as exc:  # noqa: BLE001 - provide user-friendly error
            st.error(f"Unable to resolve addresses: {exc}")
            st.stop()

        graph = loader.graph
        if graph is None:
            st.error("Failed to load the OpenStreetMap graph. Please try again.")
            st.stop()

        try:
            start_node = loader.get_nearest_node(start_coords)
            end_node = loader.get_nearest_node(end_coords)
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()

        road_graph = RoadGraph(graph, weight_attr=weight_attr)
        astar = AStar(road_graph)
        with st.spinner("Searching for the optimal path..."):
            path, cost = astar.find_path(start_node, end_node)

        if not path:
            st.warning("No path found between the selected points.")
            st.stop()

        metrics = loader.calculate_path_metrics(path)
        coordinates = loader.path_to_coordinates(path, include_edge_geometry=include_geometry)

        st.success("Route computed successfully!")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Path length", format_distance(metrics.distance_m))
        with col_b:
            st.metric("Estimated travel time", format_time(metrics.travel_time_s))
        with col_c:
            st.metric("Accumulated cost", format_primary_cost(weight_attr, cost))

        route_map = create_route_map(
            coordinates,
            graph=graph if include_geometry else None,
            start_name="Start",
            end_name="Destination",
            color=color,
        )
        if route_map is not None:
            html(route_map._repr_html_(), height=620)  # type: ignore[arg-type]

        with st.expander("Downloaded network info"):
            info = loader.get_graph_info()
            if info:
                st.write(
                    f"**Area:** {info.get('place_name', place)}\n"
                    f"**Nodes:** {info.get('num_nodes', 'N/A'):,}\n"
                    f"**Edges:** {info.get('num_edges', 'N/A'):,}"
                )
            else:
                st.write("No metadata available for the loaded graph.")

        st.caption(
            "Data © OpenStreetMap contributors — routing powered by OSMnx, NetworkX and Streamlit."
        )


if __name__ == "__main__":
    main()
