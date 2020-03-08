function findCountry(countries, wpx_to_find) {

	for (var i = 0; i < countries.length; i++) {
    		if (countries[i].WPX == wpx_to_find) {
        		return countries[i];
    			};
	};

};

function transcodeArea(info){
	if (info != undefined) {
		var new_info=info;
		if (new_info.areacode != undefined) {
			new_info.areacode=new_info.areacode.replace('UK','GB');
			new_info.areacode=new_info.areacode.replace('FL','FI');
		};
		return new_info;
	} else {
		return undefined;
	};
};
function buildHtmlTable(selector,data,rl,countries) {
	//rows
	var myRows=new Array();

	$(selector).empty();
	for (var i = 0; i < data.length; i++) {

         myRows[i]=data[i].rowid;
		var row$=$('<tr id="'+data[i].rowid+'"/>');
		var found = rl.find(element => element ==data[i].rowid);
		if ( found == undefined && rl.length > 0) {
			row$=$('<tr class="table-primary" id="'+data[i].rowid+'"/>');
		};

		var country=findCountry(countries, data[i].spotdxcc);
		//var dx_info=transcodeArea(callsign.getAmateurRadioInfoByCallsign(data[i].dx));
		row$.append($('<td/>').html('<a href="https://www.qrz.com/db/'+data[i].de+ '" target="_blank" rel="noopener"><i class="fas fa-search" aria-label="'+data[i].de+'"></i></a><span>&nbsp'+data[i].de+'</span>'));
		var freq = Intl.NumberFormat('it-IT', { style: 'decimal' }).format(data[i].freq);
		row$.append($('<td/>').html('<span class="badge badge-warning" style="width: 65px">'+freq+'</span>'));
		row$.append($('<td/>').html('<a href="https://www.qrz.com/db/'+data[i].dx+ '" target="_blank" rel="noopener"><i class="fas fa-search" aria-label="'+data[i].dx+'"></i></a><span>&nbsp'+data[i].dx+'</span>'));
		try {
  		//	row$.append($('<td/>').html('<a href="#" data-toggle="tooltip" title="'+dx_info.area+'"><img src="https://www.countryflags.io/'+dx_info.areacode+'/shiny/24.png"></a>'));
  			row$.append($('<td/>').html('<a href="#" data-toggle="tooltip" title="'+country.country+'"><img src="https://www.countryflags.io/'+country.ISO+'/shiny/24.png" alt="'+country.country+'"></a>'));
		} catch (err) {
			row$.append($('<td/>'));
		};
		row$.append($('<td class="d-none d-lg-table-cell d-xl-table-cell"/>').html(data[i].comm));
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
		tm=hh+':'+mi;
		dt=dd+'/'+mo+'/'+yy;
		row$.append($('<td/>').html(tm));
		row$.append($('<td class="d-none d-lg-table-cell d-xl-table-cell"/>').html(dt));
    		$(selector).append(row$);
   	}
	return Array.from(myRows);
};
function mySearch(event) {

	event.preventDefault();
	myTimer(); //force the call of query 

};

function myTimer() {
	var request = new XMLHttpRequest()

	selectedBands = [].map.call(document.getElementById('band').selectedOptions, option => option.value);
	selectedDEre = [].map.call(document.getElementById('de_re').selectedOptions, option => option.value);
	selectedDXre = [].map.call(document.getElementById('dx_re').selectedOptions, option => option.value);

	//construct query parameters
	var qryBands='';
	var qryAll='';
	if (selectedBands.length < 14) {
		qryBands= selectedBands.map(function(el, idx) {
	    		return 'b=' + el;
		}).join('&');
	};

	var qryDEre='';
	if (selectedDEre.length < 7) {
		qryDEre = selectedDEre.map(function(el, idx) {
	    		return 'e=' + el;
		}).join('&');
	};
	if (qryBands && qryDEre){
		qryAll=qryBands.concat('&'.concat(qryDEre));
	} else {
		qryAll=qryBands.concat(qryDEre);
	};

	var qryDXre='';
	if (selectedDXre.length< 7) {
		qryDXre = selectedDXre.map(function(el, idx) {
	    		return 'x=' + el;
		}).join('&');
	};

	if (qryAll && qryDXre) {
		qryAll=qryAll.concat('&'.concat(qryDXre));
	} else {
		qryAll=qryAll.concat(qryDXre);
	};

	// Open a new connection, using the GET request on the URL endpoint
	var qryString='spotlist';
	if (!!qryAll){
		qryString=qryString.concat('?'.concat(qryAll));
	};

	request.open('GET', qryString, true)
	//when received data, constructs the tables
	request.onload = function(){
		try {
			rows_list=buildHtmlTable('#bodyspot',JSON.parse(this.response),rows_list,my_countries.country_codes );
		} catch (err) {
			console.log(this.response);
		}
	}
	request.send()
};
