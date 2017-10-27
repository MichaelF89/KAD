<html>
<head>
	<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Search</title>
<style>
	#map {
		height: 200px;
		width: 50%;
	}
	body {
    font-family: "Lato", sans-serif;
	color: white;
	background-color: #011a46;
	}
</style>
</head>
<body>
<?php
  header("Content-type: text/html");
  
  /* ARC2 static class inclusion */
  include_once('semsol/ARC2.php');  
 
  $dbpconfig = array(
  "remote_store_endpoint" => "http://localhost:5820/KaDMerged/query",
   );
 
  $store = ARC2::getRemoteStore($dbpconfig); 
  if ($errs = $store->getErrors()) {
     echo '<h1>getRemoteStore error<h1>' ;
  }
 
  $query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX movie: <http://data.linkedmdb.org/resource/movie/>

SELECT  ?actor ?nmovie ?genre ?rt
  WHERE {
    ?movie rdf:type movie:film ;
           rdfs:label "'. $_POST["movie"] .'",?nmovie ;
           movie:has_actor/movie:actor_name ?actor .
     OPTIONAL {?movie movie:runtime ?rt .}
     OPTIONAL {?movie movie:genre/movie:genre_name ?genre .
    }}';
 
 /* execute the query */
  $rows = $store->query($query, 'rows'); 
 
    if ($errs = $store->getErrors()) {
       echo "Query errors" ;
       print_r($errs);
    }
 
    /* display the results in an HTML table */
	echo '<h1> '. $rows[0]["nmovie"] .'</h1>';
	echo ' <div id="map"></div> ';
	if (!empty($rows[0]["genre"])){
		echo '<p>Genre: ' . $rows[0]["nmovie"] .'</p>';}
	if (!empty($rows[0]["rt"])){
		echo '<p>Runtime: ' . $rows[0]["rt"] . ' minutes</p>';}
	echo '<p>Actors: ';
    foreach( $rows as $row ) { 
		echo $row["actor"] .', ';}
	echo '</p>';
	
  $query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX movie: <http://data.linkedmdb.org/resource/movie/>
PREFIX ex: <http://www.example.org/KnowledgeData/FinalAssignment/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?nloc ?long ?lat
  WHERE {
    ?movie rdf:type movie:film  ;
           rdfs:label "'. $_POST["movie"] .'" ;
     	   movie:featured_film_location/owl:sameAs ?loc.
	?loc rdfs:label ?nloc ;
		 ex:long ?long ;
		 ex:lat ?lat .}';
  
 /* execute the query */
  $rows = $store->query($query, 'rows'); 

    if ($errs = $store->getErrors()) {
       echo "Query errors" ;
       print_r($errs);
    }  
if (!empty($rows)){
	echo '<p>Location(s): ';
	foreach( $rows as $row ) { 
		echo $row["nloc"] .', ';}
	echo '</p> <script>
      function initMap() {
		var myLatLng = {lat: '. $rows[0]["lat"].', lng: '. $rows[0]["long"] .'};
        map = new google.maps.Map(document.getElementById("map"), {
          zoom: 4,
          center: myLatLng
        });';
	/* set id value */
	$id = 1;
	 foreach( $rows as $row ) { 
	 echo 'var latLng'.$id.' = {lat: '. $rows["lat"].', lng: '. $rows["long"] .'};
          var marker'.$id.' = new google.maps.Marker({
            position: latLng'.$id.',
            map: map,
			title:"'.$row["nloc"].'"
	           }); ';
    $id= $id + 1;}
	echo '} ';}
	
if (empty($rows)){
	echo 'It does work in Stardog, even without reasoning: '. $query ;}

?>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD52vGx44rARHAb8EhPhD-1I6p49IK0YmI&callback=initMap">
</script>
</body>
</html>