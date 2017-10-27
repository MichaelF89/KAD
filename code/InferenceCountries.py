from sys import argv
from rdflib import Graph, RDF, Namespace, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib.namespace import XSD

g = Graph()

def main(file):
# Define Namespaces
	MOVIEONTOLOGY = Namespace('http://www.movieontology.org/2009/10/01/movieontology.owl#')
	g.bind('movieontology',MOVIEONTOLOGY)
	OWL = Namespace('http://www.w3.org/2002/07/owl#')
	g.bind('owl',OWL)
	WD = Namespace('http://www.wikidata.org/entity/')
	g.bind('wd',WD)
	a = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
	
# Define Endpoints
	KAD = "http://localhost:5820/MergedKaD/query"
	wd = "https://query.wikidata.org/sparql"
	
# Define Queries
	L = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX movieontology: <http://www.movieontology.org/2009/10/01/movieontology.owl#>

			SELECT ?country WHERE {{
			  ?country rdf:type/rdfs:subClassOf* movieontology:Territory .
			  }} """
			  
	W = """	PREFIX wd: <http://www.wikidata.org/entity/>
			PREFIX wdt: <http://www.wikidata.org/prop/direct/>
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

			SELECT DISTINCT ?country WHERE {{
			  ?country ( rdfs:label | skos:altLabel ) "{val}"@en .
				FILTER EXISTS {{ ?country ^wdt:P17 ?o .}}
				FILTER NOT EXISTS {{?country wdt:P31 wd:Q3024240 .}}
			  }} """

# Ophalen Landen uit lokale Endpoint
	results = sparql(KAD,L)
	for result in results["results"]["bindings"]:
		cou = str(result["country"]["value"])[58:]
		country = cou.replace("_", " ")
		wresults = sparqlval(wd,W,country)
		if not wresults["results"]["bindings"]:
			print ("No Result found for:"+country)
		else:
			g.add (( MOVIEONTOLOGY[cou], a, OWL["NamedIndividual"] ))
			for wresult in wresults["results"]["bindings"]:
					if "country" in wresult:
						g.add (( MOVIEONTOLOGY[cou], OWL["sameAs"], URIRef(wresult["country"]["value"]) ))
						g.add (( URIRef(wresult["country"]["value"]), a, OWL["NamedIndividual"] ))
#						print ("Inference made between "+country+" and "+wresult["country"]["value"])

	save(file)
	
#Opslaan Graph
def serialize():
    print g.serialize(format='turtle')

def save(filename):
    with open(filename, 'w') as f:
        g.serialize(f, format='turtle')
			  
def sparql(endpoint, q):
	endp = SPARQLWrapper(str(endpoint))
	endp.setQuery(q)
	endp.setReturnFormat(JSON)
	return endp.query().convert()	
	
def sparqlval(endpoint, q, location):
	endp = SPARQLWrapper(str(endpoint))
	endp.setQuery(q.format(val=location))
	endp.setReturnFormat(JSON)
	return endp.query().convert()

if __name__ == '__main__':
    main(argv[1])