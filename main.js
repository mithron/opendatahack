$(document).ready(function() {

     //  var legendControl = L.control.legend({
     //        autoAdd: false
     //   }).addTo(map);

	

		var lineWeight1m = new L.LinearFunction(new L.Point(50000, 1), new L.Point(1000000, 12));
		var lineWeight50m = new L.LinearFunction(new L.Point(1000001, 12), new L.Point(50000000, 25));
		var lineColor1m = new L.HSLHueFunction(new L.Point(50000, 120), new L.Point(1000000, 10), {outputLuminosity: '60%'});
		var lineColor50m = new L.HSLHueFunction(new L.Point(1000001, 10), new L.Point(50000000, 0), {outputLuminosity: '60%'});

		var lineColor = new L.PiecewiseFunction([lineColor1m, lineColor50m]);
		var lineWeight = new L.PiecewiseFunction([lineWeight1m, lineWeight50m]);
		
		var firmColor = new L.HSLHueFunction(new L.Point(0, 260), new L.Point(1024, 0),
						{outputLuminosity: '40%', oddity:0, preProcess: function(value) {
							if (this.options.oddity == 1){
								this.options.oddity = 0;
								value = 1024 - value;
                                if(value<0) {return 0-value;}
                                else {	return value; }
								}
							else { this.options.oddity = 1; return value ;}							
							}
						});
		
          for(var i=0; i<schoolData.length; i++) {
	   //  for(var i=0; i<10; i++) {           
                var group = L.layerGroup();
                var colorCounter = 0;
                var options= { data: { }, chartOptions: {},
                    weight: 1, radius: 36, fillOpacity: 1,
                    rotation: 0.0, position: { x: 0, y: 0 },
				    tooltipOptions: {
							iconSize: new L.Point(120, 100),
							iconAnchor: new L.Point(-5, 64)
							},                    
                    barThickness: 26
                };

                for(var k = 0; k <contdata.length; k++) {				 
                    if(contdata[k].school_inn === schoolData[i].inn) {                       
                        options.data["'" + contdata[k].supplier_name+ "'"] = contdata[k].supplier_summ;
						//var dataColor = lineColor.evaluate(contdata[k].supplier_summ);
						var dataColor = firmColor.evaluate(colorCounter);
                        colorCounter = colorCounter + 10;
						var text = contdata[k].supplier_name + " - Контракт на " + contdata[k].supplier_summ + " рублей";
						var dataWeight = lineWeight.evaluate(contdata[k].supplier_summ);
						options.chartOptions["'"+ contdata[k].supplier_name+ "'"] =
                           { color: dataColor,
                            fillcolor: dataColor,						
                             minValue: 0, maxValue: 50000000                         
                            } ;
                        var arcedPolyline = new L.ArcedPolyline([[schoolData[i].lat,schoolData[i].lng],
                                    [contdata[k].supplier_lat,contdata[k].supplier_lng] ], {
                                //        distanceToHeight: new L.LinearFunction([0, 0], [4000, 400]),
								        fillColor: dataColor, 
										color: dataColor,
								       weight: dataWeight, displaytext: text });
						arcedPolyline.bindPopup(text, {autoPanPadding: L.point(300, 200) });
						arcedPolyline.on("click", function(e) {
							e.target.openPopup();
						});
						arcedPolyline.on("popupclose", function(e) {
								map.setView([55.75, 37.63], 10);
						});
						/*
						arcedPolyline.on("mouseover", function(e) {
								console.log(e.target);
								
						});
*/

                        group.addLayer(arcedPolyline);
                    }                 
				}                
                
				var marker = new L.PieChartMarker(new L.LatLng(schoolData[i].lat,schoolData[i].lng),
                               options);                            
				marker.on("click", function(e) {
					console.log(e.target);
					sidebar.setContent(e.target.toString());
					sidebar.show();
					});				
                if (group.getLayers() != 0) {
					group.addLayer(marker); 					
					if(i===0) { group.addTo(map); }
                    layerControl.addOverlay(group, schoolData[i].kratk_name, {groupName : "Школы Москвы", expanded:true});
				}                
             }

        map.on("overlayadd", function(e) { map.setView([55.75, 37.63], 10);})
		map.fire("dataload");
/*

// utility functions - not needed now
	
        var getSchoolByName= function(name) {
            for(var i=0; i<schoolData.length; i++) {
                if(schoolData[i].kratk_name == name) {
                    return schoolData[i]; }
            }
        }

		// strange function for getting location for layer L.Graph
		
        var getLocation = function (context, locationField, fieldValues, callback) {
            var key = fieldValues[0];
            var school = getSchoolByName(key);
            var location;

            if (school) {
                var latlng = new L.LatLng(Number(school.lat), Number(school.lng));

                location = {
                    location: latlng,
                    text: key,
                    center: latlng
                };
            }
           // console.log("Got coords! " + location.text + " = " + location.center);
            return location;
        };
        for(var i=0; i<2; i++) {
          if (schoolData[i].lat) {
            L.marker([schoolData[i].lat, schoolData[i].lng]).addTo(map);
            var key = schoolData[i].label;
            console.log("-----------------------------------Going for key " +key);

            var connectLayer = new L.Graph(schoolData, {
                recordsField: null,
                locationMode: L.LocationModes.CUSTOM,
                fromField: 'label',
                toField: 'label',
                codeField: null,
                getLocation: getLocation,
                getEdge: L.Graph.EDGESTYLE.ARC,
                includeLayer: function (record) {
                    return record.label != key;
                },
                setHighlight: function (style) {
                    style.opacity = 1.0;

                    return style;
                },
                unsetHighlight: function (style) {
                    style.opacity = 0.8;

                    return style;
                },
                layerOptions: {
                    fill: false,
                    opacity: 0.8,
                    weight: 0.5,
                    fillOpacity: 1.0,
                    distanceToHeight: new L.LinearFunction([0, 5], [1000, 200])
                },
                legendOptions: {
                    width: 200,
                    numSegments: 5,
                    className: 'legend-line'
                },
                tooltipOptions: {
                    iconSize: new L.Point(80, 64),
                    iconAnchor: new L.Point(-5, 64),
                    className: 'leaflet-div-icon line-legend'
               },
                displayOptions: {
                    cnt: {
                        weight: new L.LinearFunction([0, 1], [schoolData.length, 14]),
                        color: new L.HSLHueFunction([0, 200], [schoolData.length, 330], {
                            outputLuminosity: '60%'
                        }), displayname: schoolData[i].kratk_name,
                    displaytext: schoolData[i].kratk_name}
//
 //
 //               },
 //               onEachRecord: function (layer, record) {
 //                   layer.bindPopup($(L.HTMLUtils.buildTable(record)).wrap('<div/>').parent().html());
                }
            });


*/


});

