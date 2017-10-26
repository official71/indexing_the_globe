# -*- coding: utf-8 -*-
from collections import defaultdict
from math import log

"""
inverted list for each key word, including tiers of lists,
with tier 0 having the most priority in matching 
"""
class InvertedList(object):
    def __init__(self, word, tiers=3):
        self.word = word
        self.tiers = tiers
        self.lists = [defaultdict(int) for _ in xrange(self.tiers)]

    def add_document(self, doc_id, weight=1, tier=0):
        if 0 <= tier < self.tiers:
            self.lists[tier][doc_id] += weight

    def list_of_tier(self, tier):
        if not 0 <= tier < self.tiers:
            return []
        else:
            return self.lists[tier].items()


class SearchEngine(object):
    """
    search engine for lexical query on cities.

    ...

    Attributes
    ----------
    tiers : int
        number of tiers that each word's inverted list has, default 3.
    inverted_lists : dict
        key: word (str), value: inverted lists of word (class InvertedList)
    df : dict
        document frequency of each word
    documents : set
        set of documents (cities) ID to avoid duplicates

    Methods
    -------
    add_city(city=City())
        put one city's lexcial info in the system.
    search(query="san francisco", k=30)
        returns the any-k results that lexically match the input query.

    """
    def __init__(self):
        self.tiers = 3
        self.inverted_lists = {}
        self.df = defaultdict(int)
        self.documents = set()

    def __invlist(self, word):
        word = word.lower()
        if not word in self.inverted_lists:
            self.inverted_lists[word] = InvertedList(word, self.tiers)
        return self.inverted_lists[word]

    """add one city into the inverted index for future searching
    Parameters
    ----------
    city : City
        city instance.
    """
    def add_city(self, city):
        if not city: return
        cid = city.geonameid
        if cid in self.documents: return
        self.documents.add(cid)

        words = set()
        # tier 0 key words: name of the city
        for s in city.name.lower().split():
            l = self.__invlist(s)
            l.add_document(cid, weight=city.population, tier=0)
            words.add(s)

        # tier 1 key words: alternate names of the city
        for name in city.alternatenames:
            for s in name.lower().split():
                l = self.__invlist(s)
                l.add_document(cid, tier=1)
                words.add(s)

        # tier 2 key words: any other string
        for s in [city.country_code, city.feature_class, city.feature_code, \
            city.admin1_code, city.admin2_code, city.admin3_code, city.admin4_code] + \
            city.timezone.split('/'):
            if s:
                s = s.lower()
                l = self.__invlist(s)
                l.add_document(cid, tier=2)
                words.add(s)

        # document frequency
        for s in words:
            self.df[s] += 1

    """search key words for cities
    Parameters
    ----------
    query : str
        query string, if there are multiple terms, separated with spaces.
    k : int
        number of cities to return, forming the any-k results

    Returns
    -------
    list[int]
        list of city ID.
    """
    def search(self, query, k=30):
        
        # comparison function of search results, type: (cid, (keyword hits, weight))
        def compare(x, y):
            r = cmp(x[1][0], y[1][0])
            if r == 0:
                r = cmp(x[1][1], y[1][1])
            return r


        if not query:
            return []
        res = []
        sets = set()
        idf = lambda w: log(float(len(self.documents))/self.df[w], 10)
        keywords = [(w, idf(w)) for w in query.lower().split() if w in self.inverted_lists]
        keywords.sort(key=lambda x:x[1], reverse=True)
        # print keywords
        for tier in xrange(self.tiers):
            res_tier = {} # result of each tier
            for word, widf in keywords:
                l = self.inverted_lists[word]
                for cid, weight in l.list_of_tier(tier):
                    delta_c, delta_w = 1.0 * widf, weight * widf
                    if not cid in res_tier:
                        res_tier[cid] = (delta_c, delta_w)
                    else:
                        c, w = res_tier[cid]
                        res_tier[cid] = (c+delta_c, w+delta_w)
            # res_tier contains the number of each cid appears in the results 
            # for each query key word, we favor those cid with more "hits" of 
            # the key words, and use the "weight" to break ties
            for cid, _ in sorted(res_tier.items(), cmp=compare, reverse=True):
                if not cid in sets:
                    sets.add(cid)
                    res.append(cid)
                    if len(res) >= k:
                        return res
        return res


