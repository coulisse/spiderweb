/*==============================================================================
 * Main javascript for all core functions of this application
 * =============================================================================*/

/*
 * Decode countries
 *
 * @param countries {json} This is the json containing all the countries 
 * @param wpx_to_find {string} The string received from the db of the cluster to decode
 */
function findCountry(countries, wpx_to_find) {

	for (var i = 0; i < countries.length; i++) {
    		if (countries[i].WPX == wpx_to_find) {
        		return countries[i];
    			};
	};

};

/*
 * Build the table with the spot
 *
 * @param selector {string} The html identifier where build the spots table
 * @param data {json} The payload with all the spots received from cluster
 * @param countries {json} This is the json containing all the countries 
 * @param callsign {string} An optional parameter with the callsign to search
 */
function buildHtmlTable(selector,data,rl,countries,callsign) {
	//rows

	var myRows=new Array();

	//get current date
	var d=new Date();
	var dd_current='00'+d.getUTCDate();
        dd_current=dd_current.substring(dd_current.length - 2, dd_current.length);
        var mo_current='00'+(Number(d.getUTCMonth())+1);
        mo_current=mo_current.substring(mo_current.length - 2, mo_current.length);
        var yy_current=d.getUTCFullYear();
	dt_current=dd_current+'/'+mo_current+'/'+yy_current;
	$(selector).empty();
	for (var i = 0; i < data.length; i++) {

		myRows[i]=data[i].rowid;
		var row$=$('<tr id="'+data[i].rowid+'"/>');
		var found = rl.find(element => element ==data[i].rowid);
		if ( callsign != undefined ) {
			if ( callsign == data[i].de ) {
				row$=$('<tr class="table-success" id="'+data[i].rowid+'"/>');
			} else if ( callsign == data[i].dx ) {
				row$=$('<tr class="table-info" id="'+data[i].rowid+'"/>');
			}
		} else if ( found == undefined && rl.length > 0) {
//		if ( found == undefined && rl.length > 0) {
			row$=$('<tr class="table-info" id="'+data[i].rowid+'"/>');
		};

		var country=findCountry(countries, data[i].spotdxcc);
		if (data[i].de == callsign) {
			de = '<b>'+data[i].de+'</b>'
		} else {
			de = data[i].de
		};
		row$.append($('<td/>').html('<a href="https://www.qrz.com/db/'+data[i].de+ '" target="_blank" rel="noopener"><i class="search" aria-label="'+data[i].de+'"></i></a><span>&nbsp'+de+'</span></b>'));

		var freq = Intl.NumberFormat('it-IT', { style: 'decimal' }).format(data[i].freq);
		row$.append($('<td/>').html('<span class="badge bg-warning text-dark badge-responsive">'+freq+'</span>'));

		if (data[i].dx == callsign) {
			dx = '<b>'+data[i].dx+'</b>'
		} else {
			dx = data[i].dx
		};


		row$.append($('<td/>').html('<a href="https://www.qrz.com/db/'+data[i].dx+ '" target="_blank" rel="noopener"><i class="search" aria-label="'+data[i].dx+'"></i></a><span>&nbsp'+dx+'</span>'));
		try {
  		//	row$.append($('<td/>').html('<a href="#" data-toggle="tooltip" title="'+country.country+'"><img class="img-flag" src="https://www.countryflags.io/'+country.ISO+'/shiny/32.png" alt="'+country.country+'"></a>'));
  			row$.append($('<td/>').html('<span class="img-flag flag-icon flag-icon-'+country.ISO.toLowerCase()+'"></span>'));
		} catch (err) {
			row$.append($('<td/>'));
		};
  		row$.append($('<td class="d-none d-lg-table-cell d-xl-table-cell"/>').html(country.country));
		row$.append($('<td class="d-none d-lg-table-cell d-xl-table-cell"/>').html(data[i].comm));
		var dt=new Date(data[i].time * 1000);
		var hh='00'+dt.getUTCHours();
		hh=hh.substring(hh.length - 2, hh.length); 
		var mi='00'+dt.getMinutes();
		mi=mi.substring(mi.length - 2, mi.length);
		var dd='00'+dt.getUTCDate();
		dd=dd.substring(dd.length - 2, dd.length);
		var mo='00'+(Number(dt.getUTCMonth())+1);
		mo=mo.substring(mo.length - 2, mo.length);
		var yy=dt.getUTCFullYear();
		tm=hh+':'+mi;
		dt=dd+'/'+mo+'/'+yy;

		//show date only if is different from current date
		if (dt == dt_current) {
			row$.append($('<td/>').html(tm))
		} else {
			row$.append($('<td/>').html('<table class="table-sm table-borderless"><tbody><tr style="background-color:transparent"><td>'+tm+'</td></tr><tr><td>'+dt+'</td></tr></tbody></table>'));
		};
    		$(selector).append(row$);
   	}

	try {
		return Array.from(myRows);
	} catch (err) {
		return;
	}
};

/*
 * Function to filter spot when pressed the search button on filter
 * This function trigger the search, also triggered by timer
 */
function mySearch(event) {

	event.preventDefault();
	myTimer(); //force the call of query 

};


/*
 * Search / Filter cluster spot based on filter settings            
 * Gets the filter values, constructs the query parameter and 
 * make the request to the server
 */
function myTimer() {
	var request = new XMLHttpRequest()

	selectedBand = [].map.call(document.getElementById('band').selectedOptions, option => option.value);
	selectedDEre = [].map.call(document.getElementById('de_re').selectedOptions, option => option.value);
	selectedDXre = [].map.call(document.getElementById('dx_re').selectedOptions, option => option.value);
	selectedMode = [].map.call(document.getElementById('mode').selectedOptions, option => option.value);

	//construct query parameters
	var qryBand='';
	var qryAll='';
	if (selectedBand.length < 14) {
		qryBand= selectedBand.map(function(el, idx) {
	    		return 'b=' + el;
		}).join('&');
	};

	var qryDEre='';
	if (selectedDEre.length < 7) {
		qryDEre = selectedDEre.map(function(el, idx) {
	    		return 'e=' + el;
		}).join('&');
	};
	if (qryBand && qryDEre){
		qryAll=qryBand.concat('&'.concat(qryDEre));
	} else {
		qryAll=qryBand.concat(qryDEre);
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

	var qryMode='';
	if (selectedMode.length < 3) {
		qryMode= selectedMode.map(function(el, idx) {
	    		return 'm=' + el;
		}).join('&');
	};
	if (qryAll && qryMode) {
		qryAll=qryAll.concat('&'.concat(qryMode));
	} else {
		qryAll=qryAll.concat(qryMode);
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

/*
 * Build the html plots           
 *
 * @param selector {string} The html identifier where put the plots           
 * @param data {array} List of the plots to show                              
 */
function buildHtmlPlots(selector,data) {
	$(selector).empty();

	//bands activity
	var contBandsActivity$=$('<div class="container justify-content-center"/>');
	contBandsActivity$.append($('<h3  class="text-center"/>').html('Band Activity'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_AF']+'.png" alt="propatation heatmap AF" srcset="/static/plots/'+data['propagation_heatmaps_AF']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_AN']+'.png" alt="propatation heatmap AN" srcset="/static/plots/'+data['propagation_heatmaps_AN']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_AS']+'.png" alt="propatation heatmap AS" srcset="/static/plots/'+data['propagation_heatmaps_AS']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_EU']+'.png" alt="propatation heatmap EU" srcset="/static/plots/'+data['propagation_heatmaps_EU']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_NA']+'.png" alt="propatation heatmap NA" srcset="/static/plots/'+data['propagation_heatmaps_NA']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_OC']+'.png" alt="propatation heatmap OC" srcset="/static/plots/'+data['propagation_heatmaps_OC']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_SA']+'.png" alt="propatation heatmap SA" srcset="/static/plots/'+data['propagation_heatmaps_SA']+'.svg">'));
	$(selector).append(contBandsActivity$);

	//qso per months
	$(selector).append($('<hr>'));
	var contQSOMonth$=$('<div class="container justify-content-center"/>');
	contQSOMonth$.append($('<img class="img-fluid" src="/static/plots/'+data['qso_months']+'.png" alt="Qso per months" srcset="/static/plots/'+data['qso_months']+'.svg">'));
	$(selector).append(contQSOMonth$);

};

/*
 * Timer for refresh the plot page 
 */
function plotsTimer() {
	var request = new XMLHttpRequest()
	request.open('GET','plotlist',true)
	request.onload = function(){
		try {
			plot_list = buildHtmlPlots('#plotlist',JSON.parse(this.response));
		} catch (err) {
			console.log(err);
			console.log(this.response);
		}
	}
	request.send()
};

/*
 * Receive a callsign by the html form and make the request to server
 */
function myCallsignSearch() {
	callsign=document.getElementById('callsignInput').value;
	//construct query parameters
	if (callsign.replace(/\s/g, "").length > 0) {
		location.href = ('/callsign.html?c=').concat((callsign.trim()).toUpperCase());
	};
};

