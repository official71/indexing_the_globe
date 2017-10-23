# Indexing the globe

## Approaches

### Proximity Query

* Given the latitude and longitude of two cities, the distance is calculated using [geopy 1.11.0](https://pypi.python.org/pypi/geopy) library.
* Preprocessing data to speed up queries: for a single query, instead of iterating through all 170k+ cities and compare their distances, search from the neighboring cities first, then iteratively expanding the searching range until we've found the results. To do so, before the server starts, the city data is read into memory and fed to the `GeoInfo` class, which stores a 90 by 90 grid that contains the cities based on their latitude and longitude, therefore neigboring cities are put into the same grid. For each query, a heap is used for sorting, and the time is to the factor of K (number of neighbors needed) instead of N (number of all cities), which is a lot faster. However this approach requires more memory to store the geographical data and more time before starting the server.
* One thing worth noticing is that when searching in the grids and it reaches the edge, for longitude it should continue searching from the other end, because longitude is continuous; while for latitude it's not.

