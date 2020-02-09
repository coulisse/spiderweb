// Builds the HTML Table.
function buildHtmlTable(selector,data,rl) {
	//rows
	var myRows=new Array();

	$(selector).empty();
	for (var i = 0; i < data.length; i++) {

                myRows[i]=data[i].rowid;
		var row$;	
		row$=$('<tr/>');
		let found = rl.find(element => element ==data[i].rowid);
		if ( found == undefined && rl.length > 0) {
			row$=$('<tr class="table-info"/>');
		};
		var de_info=callsign.getAmateurRadioInfoByCallsign(data[i].de);
		var dx_info=callsign.getAmateurRadioInfoByCallsign(data[i].dx);
		row$.append($('<td/>').html('<a href="https://www.qrz.com/db/'+data[i].de+ '" target="_blank"><i class="fas fa-search"></i></a><span>&nbsp'+data[i].de+'</span>'));
		try {
			row$.append($('<td/>').html('<a href="#" data-toggle="tooltip" title="'+de_info.area+'"><img src="https://www.countryflags.io/'+de_info.areacode+'/shiny/24.png"></a>'));
		} catch (err) {
			row$.append($('<td/>'));
		};

		var freq = data[i].freq.toString().replace(/\./gi, ",");
		row$.append($('<td/>').html(freq));
		row$.append($('<td/>').html('<a href="https://www.qrz.com/db/'+data[i].dx+ '" target="_blank"><i class="fas fa-search"></i></a><span>&nbsp'+data[i].dx+'</span>'));
		try {
			row$.append($('<td/>').html('<a href="#" data-toggle="tooltip" title="'+dx_info.area+'"><img src="https://www.countryflags.io/'+dx_info.areacode+'/shiny/24.png"></a>'));
		} catch (err) {
			row$.append($('<td/>'));
		};
		row$.append($('<td/>').html(data[i].comm));
		var dt=new Date(data[i].time * 1000);
		var hh='00'+dt.getUTCHours();
		hh=hh.substring(hh.length - 2, hh.length); 
		var mi='00'+dt.getMinutes();
		mi=mi.substring(mi.length - 2, mi.length);
		var dd='00'+dt.getDate();
		dd=dd.substring(dd.length - 2, dd.length);
		var mo='00'+(Number(dt.getUTCMonth())+1);
		mo=mo.substring(mo.length - 2, mo.length);
		var yy=dt.getUTCFullYear();
		dt=hh+':'+mi+' '+dd+'/'+mo+'/'+yy;
		row$.append($('<td/>').html(dt));
      		$(selector).append(row$);
    	}
	return Array.from(myRows);
};


function myTimer() {
	var request = new XMLHttpRequest()

	// Open a new connection, using the GET request on the URL endpoint
	request.open('GET', 'spotlist', true)
	request.onload = function(){
			rows_list=buildHtmlTable('#bodyspot',JSON.parse(this.response),rows_list );
		}
	request.send()
};
