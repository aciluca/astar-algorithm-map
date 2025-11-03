"""Streamlit interface for exploring A* routing on OpenStreetMap data."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import folium
import osmnx as ox
import streamlit as st
from streamlit.components.v1 import html
from streamlit_folium import st_folium

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

LOADER_STATE_KEY = "map_loader"
LOADER_PARAMS_STATE_KEY = "map_loader_params"
START_NODE_KEY = "start_node"
END_NODE_KEY = "end_node"
START_COORDS_KEY = "start_coords"
END_COORDS_KEY = "end_coords"
CLICK_MODE_KEY = "click_mode"

LoaderParams = Tuple[str, str, bool, bool, float]


@st.cache_resource(show_spinner=False)
def load_map_loader(
    place: str,
    network_type: str,
    simplify: bool,
    retain_all: bool,
    max_edge_length_m: float,
) -> MapLoader:
    """Download (or retrieve from cache) an OpenStreetMap graph for ``place``."""

    loader = MapLoader()
    loader.load_map(
        place_name=place,
        network_type=network_type,
        simplify=simplify,
        retain_all=retain_all,
        densify_max_length_m=max_edge_length_m,
    )
    return loader


def reset_waypoints() -> None:
    """Clear any stored start/end nodes from the Streamlit session state."""

    for key in (START_NODE_KEY, END_NODE_KEY, START_COORDS_KEY, END_COORDS_KEY):
        st.session_state.pop(key, None)
    st.session_state[CLICK_MODE_KEY] = "Start point"


def ensure_click_mode_default() -> None:
    if CLICK_MODE_KEY not in st.session_state:
        st.session_state[CLICK_MODE_KEY] = "Start point"


def get_cached_loader(
    place: str,
    network_type: str,
    simplify: bool,
    retain_all: bool,
    max_edge_length_m: float,
    *,
    force_reload: bool = False,
) -> MapLoader:
    """Return a ``MapLoader`` matching the selected parameters, caching per session."""

    params: LoaderParams = (place, network_type, simplify, retain_all, max_edge_length_m)
    cached_params: Optional[LoaderParams] = st.session_state.get(LOADER_PARAMS_STATE_KEY)  # type: ignore[assignment]
    loader: Optional[MapLoader] = st.session_state.get(LOADER_STATE_KEY)

    if force_reload or loader is None or cached_params != params:
        loader = load_map_loader(place, network_type, simplify, retain_all, max_edge_length_m)
        st.session_state[LOADER_STATE_KEY] = loader
        st.session_state[LOADER_PARAMS_STATE_KEY] = params
        reset_waypoints()

    return loader


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


def render_interactive_map(loader: MapLoader) -> Optional[Dict[str, object]]:
    """Render the densified road network and return the map interaction payload."""

    graph = loader.graph
    if graph is None:
        return None

    base_map = ox.plot.plot_graph_folium(
        graph,
        tiles="cartodbpositron",
        weight=2,
        color="#6c757d",
        opacity=0.6,
    )

    start_coords = st.session_state.get(START_COORDS_KEY)
    if start_coords:
        folium.Marker(
            location=list(start_coords),
            tooltip="Start point",
            icon=folium.Icon(color="green", icon="play"),
        ).add_to(base_map)

    end_coords = st.session_state.get(END_COORDS_KEY)
    if end_coords:
        folium.Marker(
            location=list(end_coords),
            tooltip="Destination",
            icon=folium.Icon(color="red", icon="flag"),
        ).add_to(base_map)

    return st_folium(
        base_map,
        height=620,
        key="interactive_map",
        return_on_click=True,
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="A* Pathfinding on OpenStreetMap",
        page_icon="⭐",
        layout="wide",
    )

    ensure_click_mode_default()

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
            "Follow curved street geometries",
            value=True,
            help="Use the geometry of each road segment so the polyline follows the actual street shape.",
        )
        simplify = st.checkbox(
            "Simplify network",
            value=True,
            help="Let OSMnx merge nodes that form straight lines for cleaner graphs.",
        )
        retain_all = st.checkbox(
            "Retain disconnected components",
            value=False,
            help="Keep isolated subgraphs instead of only the largest connected component.",
        )
        node_spacing = st.slider(
            "Spacing between generated nodes (metres)",
            min_value=0.5,
            max_value=10.0,
            value=1.0,
            step=0.5,
            help=(
                "Edges are subdivided so no segment is longer than this distance. "
                "Smaller values create more intermediate nodes but require more memory."
            ),
        )
        color = st.color_picker("Route colour", value="#1d6be3")
        load_network = st.button("Preload map data", use_container_width=True)
        compute_route = st.button("Calculate route", type="primary", use_container_width=True)

    place_clean = place.strip()
    params: LoaderParams = (place_clean, network_key, simplify, retain_all, node_spacing)

    loader: Optional[MapLoader] = None
    if load_network:
        if not place_clean:
            st.error("Please provide an area to download from OpenStreetMap.")
        else:
            try:
                with st.spinner("Loading OpenStreetMap data..."):
                    loader = get_cached_loader(
                        place_clean,
                        network_key,
                        simplify,
                        retain_all,
                        node_spacing,
                        force_reload=True,
                    )
            except RuntimeError as exc:
                st.error(str(exc))
                loader = None
    else:
        cached_params: Optional[LoaderParams] = st.session_state.get(LOADER_PARAMS_STATE_KEY)  # type: ignore[assignment]
        if cached_params == params:
            loader = st.session_state.get(LOADER_STATE_KEY)

    st.subheader("Waypoints")
    input_mode = st.radio(
        "Select how to provide the start and end points",
        options=["Addresses", "Coordinates", "Interactive map"],
        horizontal=True,
    )

    start_input: Tuple[float, float] | str | None = None
    end_input: Tuple[float, float] | str | None = None

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
        start_input = start_address
        end_input = end_address
    elif input_mode == "Coordinates":
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
    else:
        st.write(
            "Click directly on the map to define the start and destination. The road network "
            "is subdivided roughly every metre so that clicks snap to realistic waypoints along "
            "the streets."
        )
        if loader is None:
            st.info("Preload the map from the sidebar to pick waypoints interactively.")
        else:
            click_mode = st.radio(
                "Map click assigns",
                options=["Start point", "Destination point"],
                horizontal=True,
                key=CLICK_MODE_KEY,
            )

            info_start, info_end, info_actions = st.columns([2, 2, 1])
            start_coords = st.session_state.get(START_COORDS_KEY)
            end_coords = st.session_state.get(END_COORDS_KEY)
            with info_start:
                st.write(
                    "**Start:** "
                    + (
                        f"{start_coords[0]:.6f}, {start_coords[1]:.6f}" if start_coords else "Not selected"
                    )
                )
            with info_end:
                st.write(
                    "**Destination:** "
                    + (
                        f"{end_coords[0]:.6f}, {end_coords[1]:.6f}" if end_coords else "Not selected"
                    )
                )
            with info_actions:
                if st.button("Clear", use_container_width=True):
                    reset_waypoints()

            map_event = render_interactive_map(loader)
            if map_event and map_event.get("last_clicked"):
                clicked = map_event["last_clicked"]
                lat = float(clicked["lat"])
                lon = float(clicked["lng"])
                try:
                    node_id = loader.get_nearest_node((lat, lon))
                    snapped_lat, snapped_lon = loader.get_node_coordinates(node_id)
                except RuntimeError as exc:
                    st.error(str(exc))
                else:
                    if click_mode == "Start point":
                        st.session_state[START_NODE_KEY] = node_id
                        st.session_state[START_COORDS_KEY] = (snapped_lat, snapped_lon)
                        if st.session_state.get(END_NODE_KEY) is None:
                            st.session_state[CLICK_MODE_KEY] = "Destination point"
                    else:
                        st.session_state[END_NODE_KEY] = node_id
                        st.session_state[END_COORDS_KEY] = (snapped_lat, snapped_lon)

    if compute_route:
        if not place_clean:
            st.error("Please provide an area to download from OpenStreetMap.")
            st.stop()

        try:
            with st.spinner("Loading OpenStreetMap data..."):
                loader = get_cached_loader(
                    place_clean,
                    network_key,
                    simplify,
                    retain_all,
                    node_spacing,
                )
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()

        graph = loader.graph
        if graph is None:
            st.error("Failed to load the OpenStreetMap graph. Please try again.")
            st.stop()

        if input_mode == "Interactive map":
            start_node = st.session_state.get(START_NODE_KEY)
            end_node = st.session_state.get(END_NODE_KEY)
            if start_node is None or end_node is None:
                st.error("Select both a start and a destination on the map before computing the route.")
                st.stop()
            start_coords = loader.get_node_coordinates(start_node)
            end_coords = loader.get_node_coordinates(end_node)
        else:
            if start_input is None or end_input is None:
                st.error("Provide both waypoints before computing the route.")
                st.stop()
            try:
                start_coords, end_coords = resolve_coordinates(input_mode, start_input, end_input)
            except Exception as exc:  # noqa: BLE001 - provide user-friendly error
                st.error(f"Unable to resolve addresses: {exc}")
                st.stop()
            start_node = loader.get_nearest_node(start_coords)
            end_node = loader.get_nearest_node(end_coords)
            st.session_state[START_NODE_KEY] = start_node
            st.session_state[END_NODE_KEY] = end_node
            st.session_state[START_COORDS_KEY] = loader.get_node_coordinates(start_node)
            st.session_state[END_COORDS_KEY] = loader.get_node_coordinates(end_node)

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
