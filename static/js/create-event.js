$(function() {
    var markers = [];
    function initAutocomplete() {
        var map = new google.maps.Map(document.getElementById('map'), {
            center: {
                lat: 33.126851,
                lng: -117.267139
            },
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
            for (var i = 0; i < places.length; i++) {
                var icon = {
                    url: places[i].icon,
                    size: new google.maps.Size(71, 71),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(17, 34),
                    scaledSize: new google.maps.Size(25, 25)
                };

                // Create a marker for each place.
                marker = new google.maps.Marker({
                    map: map,
                    title: places[i].name,
                    position: places[i].geometry.location,
                    dragable: true
                });
                markers.push(marker);
                var addListener = function (i) {
                    google.maps.event.addListener(markers[i], 'click', function() {
                        var thisMarker = markers[i];
                        for (var y = 0; y < markers.length; y++) {
                            if (y != i)
                                markers[y].setMap(null);
                        }
                        markers = [];
                        markers.push(thisMarker);
                    });
                }
                addListener(i);
                // var addListener = function (i) {
                //
                // }
                // addListener(i);
                if (places[i].geometry.viewport) {
                    // Only geocodes have viewport.
                    bounds.union(places[i].geometry.viewport);
                } else {
                    bounds.extend(places[i].geometry.location);
                }
            }
            map.fitBounds(bounds);
        });
        google.maps.event.addListener(map, 'click', function(event) {
            placeMarker(event.latLng);
        });

        function placeMarker(location) {
            if (markers.length >= 1) {
                markers.forEach(function(marker) {
                    marker.setMap(null);
                });
                markers = [];
            }
            var marker = new google.maps.Marker({
                position: location,
                map: map,
                draggable: true
            });
            markers.push(marker);
        }
    }

    initAutocomplete();

    $('#submitButton').click(function() {
        //get lat longitude
        if(markers.length>1)
            alert("Please click the marker you would like to pick");
        else if(markers.length<1)
            alert("Please click and place a marker, or search for a location");
        else {
            var latitude = markers[0].position.lat();
            var longitude = markers[0].position.lng();
            var groupId = $('#groupid').val();
            var description = $('#description').val();
            if(description == ""){
                alert("Please enter description of event!");
                return;
            }
            var name = $('#name').val();
            if(name == ""){
                alert("Please enter name of event!");
                return;
            }
            var date = document.getElementById("date").value;
            if(date == ""){
                alert("Please enter date of event!");
                return;
            }
            $.ajax({
                    url: "/createEvent",
                    type: "POST",
                    data: JSON.stringify({latitude:latitude,
                                          longitude: longitude,
                                          groupId: groupId,
                                          description: description,
                                          name: name,
                                          date: date
                                         }),
                    contentType: "application/json",
                    success: function(data){
                        alert("Success");
                        window.location.href="http://localhost:5000/home";
                    },
                    error: function(data){
                        alert("Please check fields");
                    }
                });
        }
    });


});
