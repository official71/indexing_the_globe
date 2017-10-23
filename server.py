#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import argparse
import os
from flask import *
from city import *
from geo import *
from search import *
from collections import defaultdict

# paths
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATA_SOURCEFILE = DATA_DIR + '/cities1000.txt'
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Flask app
app = Flask(__name__, template_folder=TEMPLATES_DIR)

# module of geographic/proximity query
geo_info = GeoInfo()

# module of lexical query
search_engine = SearchEngine()

# data of all cities
data = defaultdict(lambda: None)



@app.route('/')
def index():
    return render_template("index.html")

# for lexical search
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    cities = []
    if query:
        query = query.encode('utf8')
        for cid in search_engine.search(query):
            city = data[cid]
            if not city: continue
            cities.append(dict(cid=city.geonameid, name=city.name, \
                cc=city.country_code, pop=city.population))
    return render_template('search.html', cities=cities, prev_query=query)

# display info of one city
@app.route('/city', methods=['GET'])
def city():
    cid = request.args.get('cid')
    if not cid:
        abort(404)
    cid = int(cid)
    if not cid in data:
        abort(404)
    c = data[cid]
    city = {'cid':c.geonameid, 'name':c.name, 'cc':c.country_code, \
        'pop':c.population, 'lat':c.latitude, 'lon':c.longitude, \
        'altnames':", ".join(c.alternatenames)}
    return render_template('city.html', city=city)

# for proximity query
@app.route('/proximity', methods=['GET'])
def proximity():
    cid = request.args.get('cid')
    if not cid:
        abort(404)
    cid = int(cid)
    if not cid in data:
        abort(404)
    city = {'cid':cid, 'name':data[cid].name, 'lat':data[cid].latitude, \
        'lon':data[cid].longitude, 'cc':data[cid].country_code}

    k = int(request.args.get('k'))
    same_country = request.args.get('same_country')
    cities = []
    for dist, c in geo_info.knearest(data[cid], k, not same_country is None):
        cc = data[c]
        cities.append(dict(dist=dist, name=cc.name, cid=cc.geonameid, 
            cc=cc.country_code, lat=cc.latitude, lon=cc.longitude))
    return render_template('proximity.html', city=city, cities=cities)


def main(host, port, debug, threaded):
    # load data into modules, preprocessing speeds up server response 
    # at the cost of slow warming up
    print "loading data into modules..."
    with open(DATA_SOURCEFILE, 'r') as f:
        count = 0
        for line in f:
            city = City(line.rstrip().split('\t'))
            data[city.geonameid] = city
            geo_info.add(city)
            search_engine.add_city(city)
            count += 1
            if count % 20000 == 0:
                print "cities loaded: {}".format(count)
        print "finished loading {} cities".format(count)

    print "starting server on %s:%d" % (host, port)
    app.run(host=host, port=port, debug=debug, threaded=threaded)


if __name__ == "__main__":
    """
    Run the server using:
        python server.py host port
    Show the help text using:
        python server.py --help
    """
    parser = argparse.ArgumentParser(description='start server for Indexing the Globe')
    parser.add_argument('host', type=str, help='host address')
    parser.add_argument('port', type=int, help='host port')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    parser.add_argument('--threaded', action='store_true', help='multi-threaed')

    args = vars(parser.parse_args())
    main(**args)
