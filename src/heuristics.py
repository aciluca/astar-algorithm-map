import math
from abc import ABC, abstractmethod

# Function to calculate Haversine distance
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the Haversine distance between two points on the Earth."""
    R = 6371000  # Radius of the Earth in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2) ** 2 + 
         math.cos(phi1) * math.cos(phi2) * 
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

class Heuristic(ABC):
    @abstractmethod
    def calculate(self, node1, node2):
        pass
    
class EuclideanHeuristic(Heuristic):
    def calculate(self, node1, node2):
        lat1, lon1 = node1
        lat2, lon2 = node2
        return haversine_distance(lat1, lon1, lat2, lon2)  # Use the function
    
class ManhattanHeuristic(Heuristic):
    def calculate(self, node1, node2):
        lat1, lon1 = node1
        lat2, lon2 = node2
        
        lat_dist = haversine_distance(lat1, lon1, lat2, lon1)  # North-South distance
        lon_dist = haversine_distance(lat1, lon1, lat1, lon2)  # East-West distance
        return lat_dist + lon_dist

class ZeroHeuristic(Heuristic):
    def calculate(self, node1, node2):
        return 0