import osmnx as ox
import networkx as nx
from typing import Tuple, Optional

class MapLoader:
    """Load and manage maps from OpenStreetMap"""
    
    def __init__(self):
        self.graph = None
        self.place_name = None
        
    def load_map(self, place_name: str, network_type: str = 'drive') -> nx.MultiDiGraph:
        """
        Load a map from OpenStreetMap for a given place name and network type.
        """
        try:
            self.place_name = place_name
            self.graph = ox.graph_from_place(place_name, network_type=network_type)
            self.graph = ox.add_edge_speeds(self.graph)
            self.graph = ox.add_edge_travel_times(self.graph)
            return self.graph
        except Exception as e:
            raise Exception(f"Error loading map: {e}")
    
    def get_nearest_node(self, point: Tuple[float, float]) -> int:
        """Find the nearest node to coordinates (lat, lon)"""
        if self.graph is None:
            raise Exception("Graph not loaded")
        return ox.distance.nearest_nodes(self.graph, point[1], point[0])  # lon, lat
    
    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """Return the coordinates (lat, lon) of a node"""
        if self.graph is None:
            raise Exception("Graph not loaded")
        node = self.graph.nodes[node_id]
        return node['y'], node['x']  # lat, lon
    
    def get_graph_info(self) -> dict:
        """Return information about the graph"""
        if self.graph is None:
            return {}
        return {
            'num_nodes': len(self.graph.nodes),
            'num_edges': len(self.graph.edges),
            'place_name': self.place_name
        }