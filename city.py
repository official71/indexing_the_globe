# -*- coding: utf-8 -*-

"""
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format
"""

class City(object):
    def __init__(self, fields):
        self.geonameid = int(fields[0])
        self.name = fields[1]
        self.asciiname = fields[2].encode('ascii')
        self.alternatenames = fields[3].split(',')
        self.latitude = float(fields[4]) if fields[4] else -1
        self.longitude = float(fields[5]) if fields[5] else -1
        self.feature_class = fields[6]
        self.feature_code = fields[7]
        self.country_code = fields[8]
        self.cc2 = fields[9]
        self.admin1_code = fields[10]
        self.admin2_code = fields[11]
        self.admin3_code = fields[12]
        self.admin4_code = fields[13]
        self.population = int(fields[14]) if fields[14] else -1
        self.elevation = int(fields[15]) if fields[15] else -1
        self.dem = int(fields[16]) if fields[16] else -1
        self.timezone = fields[17]
        self.modification_date = fields[18]

    def __str__(self):
        res = "city id: {}, name: {} (ascii: {}), lat: {}, lon: {}, cc: {}, pop: {}, tz: {}".format(
            self.geonameid, self.name, self.asciiname, self.latitude, self.longitude, 
            self.country_code, self.population, self.timezone)
        # res += ", alternate names ({}): [{}]".format(len(self.alternatenames), 
        #     ', '.join(self.alternatenames))
        return res


