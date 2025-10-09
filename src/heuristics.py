import math
from abc import ABC, abstractmethod

class Heuristic(ABC):
    @abstractmethod
    def calculate(self, node1, node2):
        pass
    
class EuclideanHeuristic(Heuristic):
    def calculate(self, node1, node2):
        lat1, lon1 = node1
        lat2, lon2 = node2
        return self._haversine(lat1, lon1, lat2, lon2)
    
    def _haversine(self, lat1, lon1, lat2, lon2):
        
        R = 6371000 # Radius of the Earth in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        deltaphi = math.radians(lat2 - lat1)
        deltalambda = math.radians(lon2 - lon1)
        a = math.sin(deltaphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(deltalambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c # Distance in meters
    
class ManhattanHeuristic(Heuristic):
    def calculate(self, node1, node2):
        lat1, lon1 = node1 # (latitude, longitude)
        lat2, lon2 = node2 # (latitude, longitude)
        
        # approximate Manhattan distance using Haversine for latitudinal and longitudinal differences
        lat_dist = self._haversine(lat1, lon1, lat2, lon1) # North-South distance
        lon_dist = self._haversine(lat1, lon1, lat1, lon2) # East-West distance
        return lat_dist + lon_dist # total manhattan distance
    
    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1) 
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_phi / 2) ** 2 +  
             math.cos(phi1) * math.cos(phi2) * 
             math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c  # distance in meters

class ZeroHeuristic(Heuristic):
    def calculate(self, node1, node2):
        return 0
# this heuristic always returns zero, effectively turning A* into Dijkstra's algorithm.