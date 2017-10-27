from sys import argv
from rdflib import Graph, RDF, Namespace, Literal, URIRef
import logging

logging.basicConfig()
g = Graph()

movie = Namespace('http://data.linkedmdb.org/resource/movie/')
g.bind('movie',movie)
oddlinker = Namespace('http://data.linkedmdb.org/resource/oddlinker/')
g.bind('oddlinker',oddlinker)
foaf = Namespace('http://xmlns.com/foaf/0.1/')
g.bind('foaf',foaf)
dbr = Namespace('http://dbpedia.org/resource/')
g.bind('dbr',dbr)
dbp = Namespace('http://dbpedia.org/property/')
g.bind('dbp',dbp)
dcterms = Namespace('http://purl.org/dc/terms/')
g.bind('dcterms',dcterms)
owl = Namespace('http://www.w3.org/2002/07/owl#')
g.bind('owl',owl)
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
g.bind('skos',skos)

def main(path):
	load(path)
	print('File Loaded')
	save(str(path)[:-2]+'ttl')
	print('File Saved')

def serialize():
    print g.serialize(format='turtle')

def save(filename):
    with open(filename, 'w') as f:
        g.serialize(f, format='turtle')
        
def load(filename):
    with open(filename, 'r') as f:
		g.load(f, format='nt') 

if __name__ == "__main__":
	main(argv[1])
