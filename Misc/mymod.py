import random
from shapely.geometry import Point
import folium


def generate_random(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)
    return points


def plot_pop_points(map_obj, number, polygon, color):
    """Generates random point objects for a polygon and plots them onto a Folium map."""
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)

    for i, point_i in enumerate(points, 0):
        folium.CircleMarker(
            [tuple(point_i.coords)[0][1], tuple(point_i.coords)[0][0]],
            radius=1,
            color=color,
            opacity=0.5,
            fill=False,
        ).add_to(map_obj)
