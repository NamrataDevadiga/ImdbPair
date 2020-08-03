$(document).ready(function() {
	clients = [
      "Ryan Gosling",
      "Emma Stone",
      "Rachel McAdams",
      "Henry Golding",
      "Kareena Kapoor",
      "Constance Wu",
      "Anne Hathaway",
      "Ryan Reynolds",
      "Josh Brolin",
      "Shannon Purser",
      "Noah Centineo",
      "Jessica Chastain",
      "Matthew McConaughey",
      "Meryl Streep",
      "Sonam Kapoor",
      "Swara Bhaskar",
      "Hrithik Roshan",
      "Abhishek Bachan",
      "Ranveer Singh",
      "Deepika Padukone",
      "Ranbir Kapoor"
	];

	// actors = {{actor_autocomplete|tojson|safe}}

	$( "#tags" ).autocomplete({
      source: clients
    });

      $( "#tags1" ).autocomplete({
      source: clients
    });

});


// <script>
//     $( function() {
//       var availableTags = {{ actor_autocomplete|tojson|safe }};
//       $( "#tags" ).autocomplete({
//           source: availableTags
//       });
//     } );
//     </script>