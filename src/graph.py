from typing import Dict, List, Tuple, Optional
import networkx as nx

class RoadGraph:
    """
    Wrapper for NetworkX graph to manage road network data.
    """
    
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        
    def get_neighbors(self, node: int) -> List[Tuple[int, float]]:
        """
        Return neighbors of a node along with edge weights (travel time).
        """
        neighbors = []
        for _, neighbor, data in self.graph.edges(node, data=True):
            weight = data.get('travel_time', data.get('length', 1)) # default to length if travel_time not available)
            neighbors.append((neighbor, weight))
        return neighbors
    
    def get_node_coordinates(self, node: int) -> Tuple[float, float]:
        """
        Get the coordinates (latitude, longitude) of a node given its ID.
        """
        node_data = self.graph.nodes[node]
        return node_data['y'], node_data['x']  # (latitude, longitude)
    
    def get_edge_weight(self, node1: int, node2: int) -> float:
        """
        Get the weight (travel time) of the edge between two nodes.
        """
        try:
            edge_data = self.graph[node1][node2][0] # get first edge data if multiple edges exist
            return edge_data.get('travel_time', edge_data.get('length', 1)) # default to length if travel_time not available
        
        except (KeyError, IndexError):
            return float('inf') # return infinity if no edge exists
        
    def get_all_nodes(self) -> List[int]:
        """
        Return a list of all node IDs in the graph.
        """
        return list(self.graph.nodes)