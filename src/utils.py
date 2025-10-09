import folium
from typing import List, Tuple
import streamlit as st 

def create_route_map(coordinates: List[Tuple[float, float]],
                     start_name: str = "Start",
                     end_name: str = "End") -> folium.Map:
    """
    Create a folium map with the given route coordinates.

    Args:
        coordinates (List[Tuple[float, float]]): A list of (latitude, longitude) tuples representing the route.
        start_name (str, optional): The name of the starting point. Defaults to "Start".
        end_name (str, optional): The name of the ending point. Defaults to "End".

    Returns:
        folium.Map: A folium map object with the route displayed.
    """
    
    if not coordinates:
        return None
    
    # Center the map around the midpoint of the route
    center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    
    m = folium.Map(location = [center_lat, center_lon], zoom_start = 13)
    
    # Add route polyline
    folium.PolyLine(
        coordinates,
        color="blue",
        weight=5,
        opacity=0.7
    ).add_to(m)
    
    # Add start and end markers
    folium.Marker(
        coordinates[0],
        popup=start_name,
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    folium.Marker(
        coordinates[-1],
        popup=end_name,
        icon=folium.Icon(color='red', icon='stop')   
    ).add_to(m)
    
    return m

def format_distance(meters: float) -> str:
    """
    Format distance in meters to a more readable string in kilometers or meters.

    Args:
        meters (float): _description_

    Returns:
        str: _description_
    """
    
    if meters < 1000:
        return f"{meters:.0f} m"
    else:
        return f"{meters / 1000:.2f} km"
    
def format_time(seconds: float) -> str:
    """
    Format time in seconds to a more readable string in minutes or hours.

    Args:
        seconds (float): Time in seconds.

    Returns:
        str: Formatted time string.
    """
    
    if seconds < 60:
        return f"{seconds:.0f} sec"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f} min"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.2f} hr {minutes:.0f} min"