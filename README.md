# Indexing the globe

## Approaches

### Proximity Query

* Given the latitude and longitude of two cities, the distance is calculated using [geopy 1.11.0](https://pypi.python.org/pypi/geopy) library.
* Preprocessing data to speed up queries: for a single query, instead of iterating through all 170k+ cities and compare their distances, search from the neighboring cities first, then iteratively expanding the searching range until we've found the results. To do so, before the server starts, the city data is read into memory and fed to the `GeoInfo` class, which stores a 90 by 90 matrix that contains the cities based on their latitude and longitude, therefore neigboring cities are put into the same grid. For each query, a heap is used for sorting, and the time is to the factor of K (number of neighbors needed) instead of N (number of all cities), which is a lot faster. However this approach requires more memory to store the geographical data and more time before starting the server.
* One thing worth noticing is that when searching in the grids and it reaches the edge, for longitude it should continue searching from the other end, because longitude is continuous; while for latitude it's not.
* Optional restrictions of searching within the same country is supported by adding extra conditions when searching.

### Lexcial Query

* Single keyword matching: for a single query word, the cities whose names matches the keyword is of highest priority in the returned results, following are those whose alternate names contain the keyword, and finally "any" string contents contain the keyword. To implement this, a *reversed index* data structure is built at the beginning before the server starts, which is a hash table that maps words to the documents (in this case cities) that contains the words. For each word, 3 tiers of lists are maintained, with tier 0 list being the most important (derived from the city names), tier 1 from the city alterante names and tier 2 from other strings. For each query, we search documents in the order of tiers and stop when *any-K* results have been found.
* Multiple keywords matching: for multiple keywords, in additional to the mechanism of single keyword matching, we also take into consideration the inversed document frequency (idf) of each query word, favoring the words with higher idf. Besides, documents (cities) that hits more keywords are preferred.
* Preprocessing data is also required, since forming the reversed index is both time and space consuming. However it significantly improves the lexical query at runtime.

## Cloud Deployment

* Since the data is structured, it may help to put it in a RDBMS, however the lexical query requires some sort of in-memory data for better performance.
* The data is also static (basically the city data does not change over time) and the application is mostly read-only, it could help by caching frequently queried terms.
* Since the service is stateless, a load balancing proxy and distributed web servers can help when single server is overloaded by requests.
