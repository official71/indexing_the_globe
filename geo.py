from heapq import *
from geopy.distance import vincenty

class GeoInfo(object):
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

    # put the city into its grid
    # @param city, type City
    def add(self, city):
        if not city: return
        r = int(max(0, (city.latitude-self.lat_min)/self.lat_precision))
        c = int(max(0, (city.longitude-self.lon_min)/self.lon_precision))
        self.grids[r][c].add((city.geonameid, city.latitude, city.longitude, city.country_code))

    # distance (in miles) between two coordinates
    def __dist(self, lat1, lon1, lat2, lon2):
        return vincenty((lat1, lon1), (lat2, lon2)).miles

    # traversing the grids, starting from grid [row][col] as the center, 
    # then its neighboring grids, then further neighbors, due to the nature 
    # of longitudes, when we reach one end of the grid horizontally, we continue 
    # from the other side (b/c lon.-180 and lon.180 are connected)
    def __neighbors(self, row, col, step):
        if 0 <= row-step < self.division:
            for c in xrange(col-step, col+step):
                if c < 0: yield (row-step, self.division+c)
                if 0 <= c < self.division: yield (row-step, c)
                if c >= self.division: yield (row-step, c-self.division)
        
        if 0 <= col+step < self.division:
            for r in xrange(row-step, row+step):
                if 0 <= r < self.division: yield (r, col+step)
        elif col+step >= self.division:
            for r in xrange(row-step, row+step):
                if 0 <= r < self.division: yield (r, col+step-self.division)
        
        if 0 <= row+step < self.division:
            for c in xrange(col+step, col-step, -1):
                if c < 0: yield (row+step, self.division+c)
                if 0 <= c < self.division: yield (row+step, c)
                if c >= self.division: yield (row+step, c-self.division)
        
        if 0 <= col-step < self.division:
            for r in xrange(row+step, row-step, -1):
                if 0 <= r < self.division: yield (r, col-step)
        elif col-step < 0:
            for r in xrange(row+step, row-step, -1):
                if 0 <= r < self.division: yield (r, self.division+col-step)
    
    # find k nearest cities
    # @param city, type City
    # @param k, type int
    # @param same_country, type boolean
    # @rtype, list[(distance(miles), city ID)]
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

