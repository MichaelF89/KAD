from sys import argv
from rdflib import Graph, RDF, Namespace, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib.namespace import XSD
import re

g = Graph()
regexnr = "[0-9]+"
regexs= "[a-zA-z]+"


def main(file):

# Define Namespace
	movie = Namespace('http://data.linkedmdb.org/resource/movie/')
	g.bind('movie',movie)
	owl = Namespace('http://www.w3.org/2002/07/owl#')
	g.bind('owl',owl)
	wd = Namespace('http://www.wikidata.org/entity/')
	g.bind('wd',wd)
	rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
	g.bind('rdfs',rdfs)
	ex = Namespace('http://www.example.org/KnowledgeData/FinalAssignment/')
	g.bind('ex',ex)
	a = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

# Define Classes for Protege
	g.add (( ex["City"], a, owl["Class"] ))
	g.add (( ex["Film_Location"], a, owl["Class"] ))
	g.add (( ex["Region"], a, owl["Class"] ))

#Define ObjectProperties for Protege
	g.add (( ex["is_Location_in"], a, owl["ObjectProperty"] ))
	g.add (( ex["is_City_in"], a, owl["ObjectProperty"] ))
	g.add (( ex["is_Region_in"], a, owl["ObjectProperty"] ))

# Define DatatypeProperties for Protege
	g.add (( ex["in_street"], a, owl["DatatypeProperty"] ))
	g.add (( ex["has_number"], a, owl["DatatypeProperty"] ))	
	g.add (( ex["long"], a, owl["DatatypeProperty"] ))
	g.add (( ex["lat"], a, owl["DatatypeProperty"] ))
	
# Define Endpoints
	lmdb = "http://localhost:5820/KadMerged/query"
	wd = "https://query.wikidata.org/sparql"
	
# Define Queries
	L = """ PREFIX movie: <http://data.linkedmdb.org/resource/movie/>
			
			SELECT DISTINCT ?loc ?locname WHERE {
				?mov movie:featured_film_location ?loc .
				?loc movie:film_location_name ?locname . }"""
	W = """ #ENDPOINT <https://query.wikidata.org/sparql>
			# The {val} variables are goint to be replaced by film_location_names from Linked Movie DataBase
			PREFIX wd: <http://www.wikidata.org/entity/>
			PREFIX wdt: <http://www.wikidata.org/prop/direct/>
			PREFIX wikibase: <http://wikiba.se/ontology#>
			PREFIX p: <http://www.wikidata.org/prop/>
			PREFIX ps: <http://www.wikidata.org/prop/statement/>
			PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
			PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX bdata: <http://www.bigdata.com/rdf#>
			PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

			SELECT DISTINCT ?item ?itemLabel ?address ?streetLabel ?number ?long ?lat ?city ?cityLabel ?region ?regionLabel ?country ?countryLabel
			WHERE 
			{{{{
			# Locaties binnen een stad/dorp muv Scholen
					?item ( rdfs:label | skos:altLabel ) "{val}"@en ;
								   wdt:P131* ?city ;
								   wdt:P625 ?geo .
				FILTER NOT EXISTS {{?item wdt:P31/wdt:P279* wd:Q2385804 .}}
					
				
			  ?city wdt:P31/wdt:P279* wd:Q486972 ;
					wdt:P17 ?country .
			  FILTER NOT EXISTS {{?city wdt:P31/wdt:P279* wd:Q5195043 .}}
			  
			  OPTIONAL {{ ?item wdt:P17 ?country ;
								wdt:P131* ?region .
						  ?region wdt:P31 wd:Q35657 .
						}}
			  
			  OPTIONAL
					{{ ?item wdt:P690 ?address .}}
			  
			 OPTIONAL
			  {{ ?item wdt:P669 ?street ;
					  p:P669 ?sf .
				?sf pq:P670 ?number .
					  }}}}
			UNION
			# Regio's die niet in een stad liggen 
			  {{
					?region ( rdfs:label | skos:altLabel ) "{val}"@en ;
									 wdt:P17 ?country ;
									 wdt:P31/wdt:P279* wd:Q15916867 ;
									 wdt:P625 ?geo .
				FILTER (!sameTerm(?region,?country)).
				}}
			UNION
			# Landen
			  {{
					?country ( rdfs:label | skos:altLabel ) "{val}"@en ;
									 wdt:P31 wd:Q6256 ;
									 wdt:P625 ?geo .
				  }}
			UNION
			# Scholen hebben andere vorm van aangeven locatie
			  {{
					?item ( rdfs:label | skos:altLabel ) "{val}"@en ;
					  wdt:P31/wdt:P279* wd:Q2385804 .

			  OPTIONAL {{?item wdt:P159 ?city ;
								p:P159 ?cq .
						  ?city wdt:P31 ?settlement ;
								wdt:P17 ?country .
						  ?settlement wdt:P279 wd:Q486972 .
						OPTIONAL {{?cq pq:P625 ?geo .}}
						OPTIONAL {{?cq pq:P969 ?address .}}
						OPTIONAL {{?cq pq:P669 ?street .}}          
						OPTIONAL {{?cq pq:P670 ?number .}}
					  }}          
					OPTIONAL {{?item wdt:P969 ?address .}}
					OPTIONAL {{?item wdt:P625 ?geo .}} 
			  
			  OPTIONAL {{?item wdt:P669 ?street ;
							   p:P669 ?sf .
						 ?sf pq:P670 ?number .
					  }}
			  OPTIONAL{{ ?item wdt:P131* ?city .
						?city wdt:P31/wdt:P279 wd:Q486972 ;
							  wdt:P17 ?country . 
						FILTER NOT EXISTS {{?city wdt:P31/wdt:P279* wd:Q5195043 .}}
					  }}
			  OPTIONAL {{ ?item wdt:P17 ?country ;
								 wdt:P131* ?region .
						 ?region wdt:P31 wd:Q35657 .
					  }}
				  }}
			  FILTER ( ?country != "" ).
			  FILTER ( isLiteral(?geo) ) .
			  BIND( REPLACE( STR(?geo), "^[^0-9\\\.-]*([-]?[0-9\\\.]+) .*$", "$1" ) AS ?long )
			  BIND( replace( STR(?geo), "^.* ([-]?[0-9\\\.]+)[^0-9\\\.]*$", "$1" ) AS ?lat )
				SERVICE wikibase:label {{ bdata:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
			  }}"""
	lresults = sparql(lmdb,L)
	for lresult in lresults["results"]["bindings"]:
		loc = lresult["loc"]["value"]
		locname = lresult["locname"]["value"]
		wresults = sparqlval(wd,W,locname)
		if wresults is None:
			print ("No Result found for:"+locname.encode('utf-8'))
		elif not wresults["results"]["bindings"]:
			print ("No Result found for:"+locname.encode('utf-8'))
		else:
			g.add (( URIRef (loc), a, owl["NamedIndividual"] ))
			for wresult in wresults["results"]["bindings"]:
				if "country" in wresult:
					g.add (( URIRef(wresult["country"]["value"]), a, owl["NamedIndividual"] ))
					g.add (( URIRef(wresult["country"]["value"]), rdfs["label"], Literal(wresult["countryLabel"]["value"], lang='en') ))
					
# Places or Schools in Cities or Regions					
					if "item" in wresult:
						g.add (( URIRef(wresult["item"]["value"]), a, owl["NamedIndividual"] ))
						g.add (( URIRef (loc), owl["sameAs"], URIRef(wresult["item"]["value"]) ))
						g.add (( URIRef(wresult["item"]["value"]), a, ex["Film_Location"] ))
						g.add (( URIRef(wresult["item"]["value"]), rdfs["label"], Literal(wresult["itemLabel"]["value"], lang='en') ))
						g.add (( URIRef(wresult["item"]["value"]), ex["long"], Literal(wresult["long"]["value"]) ))	
						g.add (( URIRef(wresult["item"]["value"]), ex["lat"], Literal(wresult["lat"]["value"]) ))	
						if "city" in wresult:
							g.add (( URIRef(wresult["city"]["value"]), a, owl["NamedIndividual"] ))
							g.add (( URIRef(wresult["city"]["value"]), a, ex["City"] ))
							g.add (( URIRef(wresult["city"]["value"]), rdfs["label"], Literal(wresult["cityLabel"]["value"], lang='en') ))
							g.add (( URIRef(wresult["item"]["value"]), ex["is_Location_in"], URIRef(wresult["city"]["value"]) ))
							g.add (( URIRef(wresult["city"]["value"]), ex["is_City_in"], URIRef(wresult["country"]["value"]) ))
							if "region" in wresult:
								g.add (( URIRef(wresult["region"]["value"]), a, owl["NamedIndividual"] ))
								g.add (( URIRef(wresult["region"]["value"]), a, ex["Region"] ))
								g.add (( URIRef(wresult["region"]["value"]), rdfs["label"], Literal(wresult["regionLabel"]["value"], lang='en') ))
								g.add (( URIRef(wresult["region"]["value"]), ex["is_Region_in"], URIRef(wresult["country"]["value"]) ))
								g.add (( URIRef(wresult["city"]["value"]), ex["is_City_in"], URIRef(wresult["region"]["value"]) ))
							if "streetLabel" in wresult:
								g.add (( URIRef(wresult["item"]["value"]), ex["in_street"], Literal(wresult["streetLabel"]["value"]) ))
								if "number" in wresult and str(wresult["number"]["value"]).isdigit():
									g.add (( URIRef(wresult["item"]["value"]), ex["has_number"], Literal(wresult["number"]["value"], datatype=XSD.integer) ))

# Split Addresses up in Streetname and Number when street and number are not known							
							elif "address" in wresult:
								ad = str(wresult["address"]["value"])
								ad = ad.split(",", 1)[0]
								if re.search(regexs,ad):
									s = re.findall(regexs,ad)
									g.add (( URIRef(wresult["item"]["value"]), ex["in_street"], Literal(" ".join(s)) ))
									if re.search(regexnr,ad):
										nr = re.search(regexnr,ad)
										g.add (( URIRef(wresult["item"]["value"]), ex["has_number"], Literal(nr.group(0), datatype=XSD.integer) ))						

# Places or Schools without Addresses and City names but within a region						
						elif "region" in wresult:
								g.add (( URIRef(wresult["region"]["value"]), a, owl["NamedIndividual"] ))
								g.add (( URIRef(wresult["region"]["value"]), a, ex["Region"] ))
								g.add (( URIRef(wresult["item"]["value"]), ex["is_Location_in"], URIRef(wresult["region"]["value"]) ))
								g.add (( URIRef(wresult["region"]["value"]), rdfs["label"], Literal(wresult["regionLabel"]["value"], lang='en') ))
								g.add (( URIRef(wresult["region"]["value"]), ex["is_Region_in"], URIRef(wresult["country"]["value"]) ))
								
#Place or Schools with only country	known
						else:
							g.add (( URIRef(wresult["item"]["value"]), ex["is_Location_in"], URIRef(wresult["country"]["value"]) ))
							
# Regions
					elif "region" in wresult:
						g.add (( URIRef(wresult["region"]["value"]), a, owl["NamedIndividual"] ))
						g.add (( URIRef(wresult["region"]["value"]), a, ex["Region"] ))
						g.add (( URIRef (loc), owl["sameAs"], URIRef(wresult["region"]["value"]) ))
						g.add (( URIRef(wresult["region"]["value"]), a, ex["Film_Location"] ))
						g.add (( URIRef(wresult["region"]["value"]), rdfs["label"], Literal(wresult["regionLabel"]["value"], lang='en') ))
						g.add (( URIRef(wresult["region"]["value"]), ex["is_Region_in"], URIRef(wresult["country"]["value"]) ))
						g.add (( URIRef(wresult["region"]["value"]), ex["long"], Literal(wresult["long"]["value"]) ))	
						g.add (( URIRef(wresult["region"]["value"]), ex["lat"], Literal(wresult["lat"]["value"]) ))
						
# Countries					
					else:
						g.add (( URIRef (loc), owl["sameAs"], URIRef(wresult["country"]["value"]) ))
						g.add (( URIRef(wresult["country"]["value"]), a, ex["Film_Location"] ))
						g.add (( URIRef(wresult["country"]["value"]), ex["long"], Literal(wresult["long"]["value"]) ))	
						g.add (( URIRef(wresult["country"]["value"]), ex["lat"], Literal(wresult["lat"]["value"]) ))
				
				else:
					print ("No Result found for:"+locname.encode('utf-8'))
# Save
	save(file)
					
# Functions to print and load a local graph.
def serialize():
    print g.serialize(format='turtle')
    
def save(filename):
    with open(filename, 'w') as f:
        g.serialize(f, format='turtle')

def sparql(endpoint, query):
	endp = SPARQLWrapper(str(endpoint))
	endp.setQuery(query)
	endp.setReturnFormat(JSON)
	return endp.query().convert()

def sparqlval(endpoint, query, location):
	try:
		endp = SPARQLWrapper(str(endpoint))
		endp.setQuery(query.format(val=location.encode('utf-8')))
		endp.setReturnFormat(JSON)
		return endp.query().convert()
	except:
		return None

if __name__ == '__main__':
    main(argv[1])