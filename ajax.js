	var lineWeight1m = new L.LinearFunction(new L.Point(50000, 1), new L.Point(1000000, 12));
	var lineWeight50m = new L.LinearFunction(new L.Point(1000001, 12), new L.Point(50000000, 25));
	var lineWeight = new L.PiecewiseFunction([lineWeight1m, lineWeight50m]);	
	var labelOffset = new L.LinearFunction(new L.Point(0, 0), new L.Point(39, -144));	
	var diagOffset = new L.LinearFunction(new L.Point(2011, -110), new L.Point(2014, 110));
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
						
    map.on("overlayadd", function(e) {
            var group = e.layer;
            var layers = group.getLayers();
			map.fire('dataloading');
            if(layers.length == 1 ) {   
                    var url = 'https://intense-journey-6292.herokuapp.com/'+ layers[0].options.inn +'/';
                    group.clearLayers();
                    $.getJSON(url, function(data) {
                        if (data != 0){                    
                           
                            var suppliers = data[0].suppliers;
                            var colorCounter = 0;
                            var options = { };

                            for (var key in data[0].suppliers) {
                                if (data[0].suppliers.hasOwnProperty(key)) {
                                    var date = data[0].suppliers[key].sign_date.split('-')[0];
                                    var dataColor = firmColor.evaluate(colorCounter);
                                    colorCounter = colorCounter + 10;
                                    var text = "<p>&nbsp;</p><h3><a href='http://schools.mithron.me/?school=" + data[0].inn + "'>" + data[0].full_name + "</a></h3><p>Контракт c " + data[0].suppliers[key].name + " на " + data[0].suppliers[key].summ + " рублей заключен в " + date + " году.</p> <p>Предмет контракта: " +data[0].suppliers[key].product_name + "</p>" + "<p>Адрес поставщика: " +data[0].suppliers[key].address + "</p><p>Расширенные сведения о контракте см. <a target='_blank' href='http://clearspending.ru/contract/"+data[0].suppliers[key].cont_id+"'>тут</a>.</p>" ;
									var text2 = "Контракт c " + data[0].suppliers[key].name + " на " + data[0].suppliers[key].summ + " рублей заключен в " + date + " году.";
									
									if(allowed) {
									
										button2 = "<button onclick='disableAudio("+'"'+"popupPlayer"+'"'+")'>Отключить озвучку</button>";
									
										var audio2 = '<audio id="popupPlayer" src=' +"'" +'http://tts.voicetech.yandex.net/generate?text=%27' + data[0].full_name + " Контракт c " + data[0].suppliers[key].name + " на " + data[0].suppliers[key].summ + " рублей заключен в " + date + " году.%27" + '&format=mp3&lang=ru-RU&speaker=zahar&key=519d3768-9302-4f28-8eab-0eb1bf9579d5'+ "'" + ' autoplay="autoplay" type="audio/mp3" preload="none"></audio></div>';
									
										text2 = audio2+text2 +button2; }

                                    var dataWeight = lineWeight.evaluate(data[0].suppliers[key].summ);
                                    var dataOffset = diagOffset.evaluate(date);
									if(allowed) {
										button = "<button onclick='disableAudio("+'"'+"sidebarPlayer"+'"'+")'>Отключить озвучку</button>" ;
										var audio = '<audio id="sidebarPlayer" src=' +"'" +'http://tts.voicetech.yandex.net/generate?text=%27' + data[0].full_name + " Контракт c " + data[0].suppliers[key].name + " на " + data[0].suppliers[key].summ + " рублей заключен в " + date + " году. Предмет контракта: " +data[0].suppliers[key].product_name + " Адрес поставщика: " +data[0].suppliers[key].address +"%27" +'&format=mp3&lang=ru-RU&speaker=zahar&key=519d3768-9302-4f28-8eab-0eb1bf9579d5'+ "'" + ' autoplay="autoplay" type="audio/mp3" preload="none"></audio></div>';
										text = audio + text + button; }
									
                                    if(typeof options[date] != "undefined"){
                                        options[date].data["'" + data[0].suppliers[key].name+ "'"] = 							data[0].suppliers[key].summ;
                                        options[date].chartOptions["'"+ data[0].suppliers[key].name+ "'"] =
                                        { color: dataColor,
                                            fillColor: dataColor,
                                            minValue: 0, maxValue: 50000000,
                                            text: text,
                                        } ;
                                    }
                                    else {
                                        options[date] = { data: { }, chartOptions: {},
                                            weight: 1, radius: 36, fillOpacity: 1,
                                            rotation: 0.0, position: { x: dataOffset, y: 0 },
                                            tooltipOptions: {
                                                iconSize: new L.Point(120, 100),
                                                iconAnchor: new L.Point(-5, 64)
                                            },
                                            barThickness: 26
                                        };
                                        // options[date].position.x = dataOffset;
                                        options[date].data["'" + data[0].suppliers[key].name+ "'"] = 							data[0].suppliers[key].summ;
                                        options[date].chartOptions["'"+ data[0].suppliers[key].name+ "'"] =
                                        { color: dataColor,
                                            fillColor: dataColor,
                                            minValue: 0, maxValue: 50000000,
                                            text: text
                                        } ;
                                    }

                                    var arcedPolyline = new L.ArcedPolyline([[data[0].lat,data[0].lng],
                                        [data[0].suppliers[key].lat,data[0].suppliers[key].lng] ], {
                                        //        distanceToHeight: new L.LinearFunction([0, 0], [4000, 400]),
                                        fillColor: dataColor,
                                        color: dataColor,
                                        weight: dataWeight, displayText: text });
                                    arcedPolyline.bindPopup(text2, {autoPanPadding: L.point(300, 200) });

                                    arcedPolyline.on("click", function(e) {
                                        e.target.openPopup();
                                    });

                                    arcedPolyline.on("popupopen", function(e) {
                                        stopAudio('popupPlayer', allowed);
                                    });

                                    arcedPolyline.on("popupclose", function(e) {
                                        map.setView([55.75, 37.63], 10);
                                    });
                                    /*
                                     arcedPolyline.on("mouseover", function(e) {
                                     console.log(e.target);

                                     });*/

                                     group.addLayer(arcedPolyline);
                                     };
                                };
                          for(i=2011;i<2015;i++){
                             if(typeof options[i] != "undefined"){
                                var marker = new L.PieChartMarker(new L.LatLng(data[0].lat,data[0].lng),
                                     options[i]);
                                marker.on("click", function(e) {
                                     sidebar.hide();
                                     sidebar.setContent(e.layer.options.chartOptions[e.layer.options.key].text);
                                     stopAudio('sidebarPlayer', allowed);
                                     sidebar.show();

                                     });
                                group.addLayer(marker);
								var hiddenMarker = new L.Marker(new L.LatLng(data[0].lat,data[0].lng), {icon: invisibleIcon}).bindLabel(i + " год", {noHide: true, offset: [diagOffset.evaluate(i)-33, 40]});
								group.addLayer(hiddenMarker);
                            }};

                            if (group.getLayers() != 0) {
									 var hiddenMarker = new L.Marker(new L.LatLng(data[0].lat,data[0].lng), {icon: invisibleIcon}).bindLabel("<a href='http://schools.mithron.me/?school=" + data[0].inn +"'>"+ data[0].full_name + "</a>", { clickable:true, noHide: true, offset: [labelOffset.evaluate(data[0].full_name.length), -70], direction: 'right'});
									 var hiddenMarker2 = new L.Marker(new L.LatLng(data[0].lat,data[0].lng), {icon: invisibleIcon}).bindLabel("Поделиться:&nbsp; <a target='_blank' href='https://vk.com/share.php?url=http://schools.mithron.me/?school="+ data[0].inn +"'> <i class='fa fa-vk'></i></a> &nbsp;&nbsp; <a target='_blank' href='https://www.facebook.com/sharer.php?u=http://schools.mithron.me/?school="+ data[0].inn +"'> <i class='fa fa-facebook-square'></i></a> &nbsp;&nbsp; <a target='_blank' href='http://twitter.com/intent/tweet?url=http://schools.mithron.me/?school="+ data[0].inn +"&text=Cколько кому платят школы Москвы. Проголосуйте http://budgetapps.ru/contest%23projects'> <i class='fa fa-twitter-square'></i></a> ", { clickable:true, noHide: true, offset: [-72, 72], direction: 'right'});
									 group.addLayer(hiddenMarker);
									 group.addLayer(hiddenMarker2);       								
                               }
							
						    map.fire('dataload');
                           }	
					else { map.fire('dataload');}
					});
             }
			 else {
				map.fire('dataload'); }
           
	});

	map.fire("dataload");