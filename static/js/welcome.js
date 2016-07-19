$(function(){
    var map;
var username = $("#username").attr('data-username');
$.ajax({
    type: "POST",
    url: "/getEvents",
    data: JSON.stringify({username:username}),
    contentType: "application/json",
    success: function(data){
        initAutocomplete(data);
    }
});

$('.deleteEvent').click(function(){
    var eventId= $(this).attr('data-event-id');
    $.ajax({
        type: "POST",
        url: "/removeEvent",
        data: JSON.stringify({eventId:eventId}),
        contentType: "application/json",
        success: function(data){
            alert("Deleted");
            location.reload();
        }
    });
});
$(".anEvent").click(function(){
    var lat = $(this).attr('data-lat');
    var lng = $(this).attr('data-lng');
    var center = new google.maps.LatLng(lat, lng);
    map.panTo(center);
});



$(".hover-event").hover(function(){
    $(this).toggleClass("list-group-item-info");
});

function initAutocomplete(eventLocations) {
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 33.126851, lng: -117.267139},
          zoom: 16,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });

        // Create the search box and link it to the UI element.
        var input = document.getElementById('pac-input');
        var searchBox = new google.maps.places.SearchBox(input);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

        // Bias the SearchBox results towards current map's viewport.
        map.addListener('bounds_changed', function() {
          searchBox.setBounds(map.getBounds());
        });

        var markers = [];
        // Listen for the event fired when the user selects a prediction and retrieve
        // more details for that place.
        searchBox.addListener('places_changed', function() {
          var places = searchBox.getPlaces();

          if (places.length == 0) {
            return;
          }

          // Clear out the old markers.
          markers.forEach(function(marker) {
            marker.setMap(null);
          });
          markers = [];

          // For each place, get the icon, name and location.
          var bounds = new google.maps.LatLngBounds();
          places.forEach(function(place) {
            var icon = {
              url: place.icon,
              size: new google.maps.Size(71, 71),
              origin: new google.maps.Point(0, 0),
              anchor: new google.maps.Point(17, 34),
              scaledSize: new google.maps.Size(25, 25)
            };

            // Create a marker for each place.
            markers.push(new google.maps.Marker({
              map: map,
              icon: icon,
              title: place.name,
              position: place.geometry.location
            }));

            if (place.geometry.viewport) {
              // Only geocodes have viewport.
              bounds.union(place.geometry.viewport);
            } else {
              bounds.extend(place.geometry.location);
            }
          });
          map.fitBounds(bounds);
        });
/*HERE IS THE CREATION OF FLAGS AND INFO WINDOWS*/////////////////////////////////////////////////////////////////////////////////
        // var addListener = function (i) {
        // google.maps.event.addListener(markers[i], 'click', function(){
        //     infos[i].open(map, markers[i]);
        // });
        // }
        var markers;
        var infos = [];
        for(var i = 0; i<eventLocations.length; i++){
            var contentString = '<h1 id="firstHeading" class="firstHeading">'+eventLocations[i]['name']+'</h1>';
            contentString += '<h3>'+ eventLocations[i]['date']+'</h3>';
            contentString += '<div id="bodyContent">'+
            '<p>'+ eventLocations[i]['description'] +'</p></div>';
            contentString += '<a target="_blank" href="https://www.google.com/maps/place/'+eventLocations[i]['lat']+','+ eventLocations[i]['lng'] +'">See on Google Maps (for directions)</a>';
            var locationToMark = {lat: eventLocations[i]['lat'], lng: eventLocations[i]['lng']};
            var infowindow = new google.maps.InfoWindow({
              content: contentString
            });
            infos.push(infowindow);
            var marker = new google.maps.Marker({
              position: locationToMark,
              map: map
            });
            markers.push(marker);
            var addListener = function (i) {
                google.maps.event.addListener(markers[i], 'click', function(){
                    infos[i].open(map, markers[i]);
                });
            }
            addListener(i);
        }

      }

});
