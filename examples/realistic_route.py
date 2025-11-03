"""Compute a realistic A* route on an OpenStreetMap network."""

from __future__ import annotations

import argparse
from pathlib import Path

from src import AStar, MapLoader, RoadGraph, create_route_map, format_distance, format_time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--place",
        default="Rome, Italy",
        help="Human-readable location to download from OpenStreetMap.",
    )
    parser.add_argument(
        "--network-type",
        default="drive",
        choices=["drive", "walk", "bike", "drive_service"],
        help="Type of road network to download.",
    )
    parser.add_argument(
        "--point",
        nargs=2,
        type=float,
        metavar=("LAT", "LON"),
        help="Optional lat/lon pair to center the download instead of --place.",
    )
    parser.add_argument(
        "--dist",
        type=int,
        default=1500,
        help="Search distance in metres when using --point.",
    )
    parser.add_argument(
        "--start",
        nargs=2,
        type=float,
        default=(41.9022, 12.4956),
        metavar=("LAT", "LON"),
        help="Latitude/longitude of the start location.",
    )
    parser.add_argument(
        "--end",
        nargs=2,
        type=float,
        default=(41.8902, 12.4922),
        metavar=("LAT", "LON"),
        help="Latitude/longitude of the destination.",
    )
    parser.add_argument(
        "--color",
        default="red",
        help="Colour of the route polyline on the exported map.",
    )
    parser.add_argument(
        "--save",
        type=Path,
        help="Optional path to save the rendered folium map as HTML.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    loader = MapLoader()
    if args.point:
        point = (args.point[0], args.point[1])
        graph = loader.load_map(point=point, dist=args.dist, network_type=args.network_type)
        location_name = f"Point @ {point[0]:.4f}, {point[1]:.4f}"
    else:
        graph = loader.load_map(place_name=args.place, network_type=args.network_type)
        location_name = args.place

    start_node = loader.get_nearest_node(tuple(args.start))
    end_node = loader.get_nearest_node(tuple(args.end))

    astar = AStar(RoadGraph(graph))
    path, cost = astar.find_path(start_node, end_node)

    if not path:
        print("No path found between the selected points.")
        return 1

    metrics = loader.calculate_path_metrics(path)
    coordinates = loader.path_to_coordinates(path, include_edge_geometry=True)

    print(f"Location: {location_name}")
    print(f"Nodes explored: {len(path)}")
    print(f"Path distance: {format_distance(metrics.distance_m)}")
    print(f"Travel time: {format_time(metrics.travel_time_s)}")
    print(f"Total cost (seconds): {cost:.2f}")

    fmap = create_route_map(
        coordinates,
        graph=graph,
        start_name="Start",
        end_name="Goal",
        color=args.color,
    )
    if args.save and fmap is not None:
        fmap.save(args.save)
        print(f"Saved route map to {args.save}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
