# A* Pathfinding Algorithm Visualization 🗺️⭐

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=OpenStreetMap&logoColor=white)](https://openstreetmap.org)

An interactive web application that visualizes the A* pathfinding algorithm on real city street networks using OpenStreetMap data.

![Demo](https://img.shields.io/badge/Demo-Live%20Visualization-blue)

## 🚀 Features

- **Real City Maps**: Load actual street networks from major cities worldwide
- **Live A* Visualization**: Watch the algorithm explore nodes in real-time
- **Interactive Controls**: Select start/end points and adjust animation speed
- **Multiple Cities**: Choose from Rome, Milan, Chicago, New York, London, Paris, Tokyo
- **Dual Visualization**: Interactive Folium maps + Matplotlib graphs

## 🏗️ How It Works

1. **Data Fetching**: Uses OSMnx to download real street network data from OpenStreetMap
2. **Graph Modeling**: Represents intersections as nodes and streets as edges
3. **A* Algorithm**: Implements A* search with Haversine distance heuristic
4. **Visualization**: Displays the algorithm's exploration process with color-coded nodes

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/astar-pathfinding-visualization.git
cd astar-pathfinding-visualization

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

```
## 📋 Requirements

streamlit>=1.28.0
osmnx>=1.6.0
networkx>=3.0
folium>=0.14.0
matplotlib>=3.7.0
numpy>=1.24.0

## 🎮 Usage

1. Select a city from the sidebar
2. Choose the area size (500-2000 meters)
3. Click "Load Map" to fetch OpenStreetMap data
4. Select start and end nodes
5. Click "Find Path with A*" to run the algorithm
6. Watch the live visualization!

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
coordinates = loader.path_to_coordinates(path)
```

### Command-line example

To generate a realistic route and export it as an interactive HTML map, run the
example script:

```bash
python examples/realistic_route.py --save rome_route.html
```

By default the script downloads the drivable network around Rome's city centre
and finds a path between Piazza Venezia and the Colosseum. You can customise the
area with `--place` or `--point LAT LON`, choose a different network type, and
provide your own start/end coordinates to inspect other routes.

## 🎯 Algorithm Details

- *A Search**: Combines actual path cost (g-score) with heuristic estimate (h-score)
- Haversine Heuristic: Uses great-circle distance for accurate geographical estimates
- Real Weights: Edge weights based on actual street lengths from OpenStreetMap

## 🏙️ Supported Cities

- Rome, Italy
- Milan, Italy
- Chicago, USA
- New York, USA
- London, UK
- Paris, France
- Tokyo, Japan

## 📁 Project Structure

```bash
astar-pathfinding/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── assets/               # Screenshots and demo files
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenStreetMap contributors for the map data
- OSMnx library for street network analysis
- Streamlit for the web framework
