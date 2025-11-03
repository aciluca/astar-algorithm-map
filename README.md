# A* Pathfinding on OpenStreetMap 🗺️⭐

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=OpenStreetMap&logoColor=white)](https://openstreetmap.org)

An interactive Streamlit application for experimenting with the A* search
algorithm on real street networks downloaded with
[OSMnx](https://osmnx.readthedocs.io/). You can explore the fastest or shortest
routes between any two points, visualise the resulting path on top of the
OpenStreetMap basemap and reuse the underlying Python API in your own projects.

## 🚀 Features

- **Streamlit front-end** – discover the algorithm through an interactive UI: pick any city, geocode addresses or paste lat/lon coordinates and compare fastest vs. shortest routes.
- **Real OpenStreetMap data** – download drivable, walkable or bikeable graphs with OSMnx and reuse them in custom experiments.
- **Reusable pathfinding core** – production-ready A* and Dijkstra implementations operating on NetworkX graphs, plus helpers to convert paths into coordinates and metrics.
- **Command-line automation** – `examples/realistic_route.py` fetches a network, computes a route and exports it as an interactive Folium map.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/astar-algorithm-map.git
cd astar-algorithm-map

# Install dependencies (ideally inside a virtual environment)
pip install -r requirements.txt
```

The requirements bundle everything needed to run the Streamlit experience: the
OpenStreetMap tooling (`osmnx`, `networkx`), map rendering (`folium`) and the UI
framework itself (`streamlit`).

## 🎮 Usage

### Streamlit application

Launch the interactive UI and open the link shown in the console (usually
http://localhost:8501):

```bash
streamlit run app.py
```

From the sidebar you can:

- Choose the **OpenStreetMap area** (by city name) and network type (drive, walk, bike, service).
- Decide whether the cost function should optimise **travel time** or **distance**.
- Toggle map preprocessing options exposed by OSMnx (graph simplification and component retention).
- Pick the **start and destination** either via address geocoding or by entering latitude/longitude pairs.
- Customise the colour of the rendered polyline and whether it should follow the true street geometry.

After clicking **Calculate route** the page displays the path metrics and renders
the result on an interactive Folium map embedded inside Streamlit.

### Command-line example

To generate a realistic route and export it as an interactive HTML map, run the
example script from the project root:

```bash
python examples/realistic_route.py --save rome_route.html
```

By default the script downloads the drivable network around Rome's city centre
and finds a path between Piazza Venezia and the Colosseum. You can customise the
area with `--place "Milano, Italy"` or `--point LAT LON`, choose a different
network type with `--network-type`, and provide your own start/end coordinates.
Run `python examples/realistic_route.py --help` to see the full list of options.

The generated polyline uses the real OpenStreetMap geometry for every road
segment, so the route hugs the actual streets instead of straight lines between
intersections.

### Programmatic usage

```python
from src import AStar, MapLoader, RoadGraph

loader = MapLoader()

# Load a drivable network around a point (lat, lon) with a 1.5 km bounding box
graph = loader.load_map(
    point=(45.4642, 9.19),  # Milan Cathedral
    dist=1500,
    network_type="drive",
)

road_graph = RoadGraph(graph)
start = loader.get_nearest_node((45.4682, 9.1810))
goal = loader.get_nearest_node((45.4559, 9.2043))

path, cost = AStar(road_graph).find_path(start, goal)
# Include the intermediate geometry points so the route follows the road shape
coordinates = loader.path_to_coordinates(path, include_edge_geometry=True)
```

#### CLI options at a glance

| Flag | Description |
| ---- | ----------- |
| `--place "City, Country"` | Download the network around a human-readable place name (default: Rome, Italy). |
| `--point LAT LON --dist 1500` | Centre the download on a latitude/longitude pair with a custom radius in metres. |
| `--network-type {drive,walk,bike,drive_service}` | Select the type of network to download from OpenStreetMap. |
| `--start LAT LON` / `--end LAT LON` | Override the default origin and destination coordinates. |
| `--save output.html` | Persist the rendered Folium map to disk. |

## 📁 Project Structure

```bash
astar-algorithm-map/
├── src/                  # A* implementation and helpers
├── examples/             # Executable examples (CLI route generator)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenStreetMap contributors for the map data
- [OSMnx](https://github.com/gboeing/osmnx) for street network analysis utilities
- [Folium](https://github.com/python-visualization/folium) for the interactive maps
