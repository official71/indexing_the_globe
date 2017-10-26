from heapq import *
from geopy.distance import vincenty

class GeoInfo(object):
    """
    Geographical information of cities for proximity query.

    ...

    Attributes
    ----------
    division : int
        latitude/longitude of the globe are divided into divsion by division grids.

    Methods
    -------
    add(city=City())
        put one city's geographical info in the system.
    knearest(city=City(), k=10, same_country=False)
        returns the k-nearest cities in distance of input city, with optional constraints of cities being in the same country.

    """
    def __init__(self, division=90):
        self.division = division

        self.lat_min = -90
        self.lat_max = 90
        self.lat_precision = float(self.lat_max - self.lat_min) / self.division

        self.lon_min = -180
        self.lon_max = 180
        self.lon_precision = float(self.lon_max - self.lon_min) / self.division

        # rows: latitude, cols: longitude
        self.grids = [[set() for _ in xrange(division)] for _ in xrange(division)]

    """add one city into the system
    Parameters
    ----------
    city : City
        city instance.
    """
    def add(self, city):
        if not city: return
        r = int(max(0, (city.latitude-self.lat_min)/self.lat_precision))
        c = int(max(0, (city.longitude-self.lon_min)/self.lon_precision))
        self.grids[r][c].add((city.geonameid, city.latitude, city.longitude, city.country_code))

    # distance (in miles) between two coordinates
    def __dist(self, lat1, lon1, lat2, lon2):
        return vincenty((lat1, lon1), (lat2, lon2)).miles

    """traversing the grids from the center
    Parameters
    ----------
    row : int
        row of the center grid
    col : int
        column of the center grid
    step : int
        distance of the searching circle to the center grid, e.g. when step = 1, we search the grids that is of distance 1 to the center

    Yields
    -------
    tuple(int, int)
        row, col of the next grid to search.
    """
    def __neighbors(self, row, col, step):
        # search grids in the row to the north of center [row, col] by the distance of step
        if 0 <= row-step < self.division:
            for c in xrange(col-step, col+step):
                # from west to east, search the row, for longitude if reaching the west-most boundary,
                # continue from the east-most boundary to the west b/c it's continuous
                if c < 0: yield (row-step, self.division+c)
                if 0 <= c < self.division: yield (row-step, c)
                # similarly, for longitude if reaching the east-most boundary, continue from west-most side
                if c >= self.division: yield (row-step, c-self.division)
        
        # search grids in the column to the east side of the center by the distance of step
        if 0 <= col+step < self.division:
            for r in xrange(row-step, row+step):
                if 0 <= r < self.division: yield (r, col+step)
        # if reaching the east-most side, continue searching from the west-most side
        elif col+step >= self.division:
            for r in xrange(row-step, row+step):
                if 0 <= r < self.division: yield (r, col+step-self.division)
        
        # search grids in the row to the south side of the center
        if 0 <= row+step < self.division:
            for c in xrange(col+step, col-step, -1):
                if c < 0: yield (row+step, self.division+c)
                if 0 <= c < self.division: yield (row+step, c)
                if c >= self.division: yield (row+step, c-self.division)
        
        # search grids in the column to the west side of the center 
        if 0 <= col-step < self.division:
            for r in xrange(row+step, row-step, -1):
                if 0 <= r < self.division: yield (r, col-step)
        elif col-step < 0:
            for r in xrange(row+step, row-step, -1):
                if 0 <= r < self.division: yield (r, self.division+col-step)
    
    """find k nearest cities
    Parameters
    ----------
    city : class City
        the city to search around.
    k : int
        number of nearest neighbors to find
    same_country : boolean
        True if results must be of the same country as input city

    Returns
    -------
    list[tuple(float, int)]
        list of the nearest cities with their distances (in miles) and ID.
    """
    def knearest(self, city, k=10, same_country=False):
        ocid, lat, lon, cc = city.geonameid, city.latitude, city.longitude, city.country_code
        row = int(max(0, (lat-self.lat_min)/self.lat_precision))
        col = int(max(0, (lon-self.lon_min)/self.lon_precision))
        heap = []
        for step in xrange(self.division):
            for r, c in self.__neighbors(row, col, step):
                for cid, lat1, lon1, cc1 in self.grids[r][c]:
                    if cid == ocid or same_country and cc != cc1: continue
                    dist = self.__dist(lat, lon, lat1, lon1)
                    if len(heap) < k:
                        # not full
                        heappush(heap, (-dist, cid))
                    elif heap[0][0] < -dist:
                        heapreplace(heap, (-dist, cid))
            if len(heap) >= k:
                break
        res = []
        while heap:
            res.append(heappop(heap))
        return [(-r[0], r[1]) for r in reversed(res)]

