import osmnx as ox
import networkx as nx
from typing import Tuple, Optional
import pandas as pd

class MapLoader:
    ### class to load and manage map data from OpensStreetMap
    
    def __init__(self):
        self.graph = None
        self.place_name = None
        
    def load_map(self, place_name: str, network_type: str = 'drive') -> nx.MultiDiGraph:
        
        """Load map data for a specified place using OSMnx.
        
        Args:
            place_name (str): Name of the place to load the map for.
            network_type (str): Type of network to load (e.g., 'drive', 'walk').
        """ 
        try:
            self.place_name = place_name
            self.graph = ox.graph_from_place(place_name, network_type=network_type)
            self.graph = ox.add_edge_speeds(self.graph) # add speed data to edges
            self.graph = ox.add_edge_travel_times(self.graph) # add travel time data to edges
            return self.graph
        except Exception as e:
            print(f"Error loading map for {place_name}: {e}")

    def get_nearest_node(self, point: Tuple[float, float]) -> int:
        """
        Get the nearest node in the graph to a given point (latitude, longitude).
        """
        if self.graph is None:  
            raise ValueError("Graph not loaded. Please load a map first.")
        
        return ox.distance.nearest_nodes(self.graph, point[1], point[0])
    
    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """
        Get the coordinates (latitude, longitude) of a node given its ID.
        """
        if self.graph is None:
            raise ValueError("Graph not loaded. Please load a map first.")
        
        node_data = self.graph.nodes[node_id]
        return (node_data['y'], node_data['x'])  #  (latitude, longitude)

    def get_graph_info(self) -> dict:
        """
        Get basic information about the loaded graph.
        """
        if self.graph is None:
            raise ValueError("Graph not loaded. Please load a map first.")
        
        return {
            "number_of_nodes": len(self.graph.nodes),
            "number_of_edges": len(self.graph.edges),
            "place_name": self.place_name
        }