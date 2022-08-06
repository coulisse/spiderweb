/********************************************************************************
 * javascript used to popolate main  table with spots            
 * ******************************************************************************/

var adxo_url='https://www.ng3k.com/misc/adxo.html'
var qrz_url='https://www.qrz.com/db/'

/**
 * Decode Announced Dx Operation (ng3k)
 *
 * @param adxo {adxo} This is the json containing all the dxo events
 * @param callsign_to_find {callsign_to_find} The callsign of the current dx line
 */
function findAdxo(adxo, callsign_to_find) {
	if (adxo) {
		for (var i = 0; i < adxo.length; i++) {
    			if (adxo[i].callsign == callsign_to_find) {
        			return adxo[i];
    			}
		}
	}
}
/**
 * Build the table with the spot
 *
 * @param selector {string} The html identifier where build the spots table
 * @param data {json} The payload with all the spots received from cluster
 * @param callsign {string} An optional parameter with the callsign to search
 */
function buildHtmlTable(selector,data,rl,callsign) {
  if  ( data != null ){

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
				row$=$('<tr id="'+data[i].rowid+'"/>');
			} else if ( callsign == data[i].dx ) {
				row$=$('<tr id="'+data[i].rowid+'"/>');
			}
		} else if ( found == undefined && rl.length > 0) {
			row$=$('<tr class="table-info" id="'+data[i].rowid+'"/>');
		}

		if (data[i].de == callsign) {
			de = '<mark>'+data[i].de+'</mark>'
		} else {
			de = data[i].de
		}
		row$.append($('<td/>').html('<a href="'+qrz_url+data[i].de+ '" target="_blank" rel="noopener"><i class="bi-search" role="button" aria-label="'+data[i].de+'"></i></a><span>&nbsp'+de+'</span></b>'));

		var freq = Intl.NumberFormat('it-IT', { style: 'decimal' }).format(data[i].freq);
		row$.append($('<td/>').html('<span class="badge bg-warning text-dark badge-responsive">'+freq+'</span>'));

		if (data[i].dx == callsign) {
			dx = '<mark>'+data[i].dx+'</mark>'
		} else {
			dx = data[i].dx
		}

		var adxo=findAdxo(my_adxo_events, data[i].dx);
		var adxo_link='<a href='+adxo_url+' target=_blank rel=noopener >NG3K Website</a>'
		if (adxo != undefined) {
			dx=dx+'&nbsp<i tabindex="0" class="bi-megaphone-fill" style="color: cornflowerblue; " role="button" aria-label="dx_operations" data-bs-container="body" data-bs-toggle="popover" data-bs-trigger="focus" data-bs-sanitize="true" data-bs-placement="auto" data-bs-html="true" data-bs-title="Announced DX Op.: '+adxo.summary+'" data-bs-content="'+adxo.description+" data from "+'&nbsp'+adxo_link+'"></i>'
		}

		row$.append($('<td/>').html('<a href="'+qrz_url+data[i].dx+ '" target="_blank" rel="noopener"><i class="bi-search" role="button" aria-label="'+data[i].dx+'"></i></a><span>&nbsp'+dx+'</span>'));
		try {
			row$.append($('<td/>').html('<span class="img-flag fi fi-'+data[i].iso+'" data-bs-container="body" data-bs-toggle="popover" data-bs-trigger="hover" data-bs-placement="left" data-bs-content="'+data[i].country+'"></span>'));
		} catch (err) {
			row$.append($('<td/>'));
		}
  		row$.append($('<td class="d-none d-lg-table-cell d-xl-table-cell"/>').html(data[i].country));
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
		}
    		$(selector).append(row$);
   	}

	$(function () {
  		$('[data-bs-toggle="popover"]').popover({
    			container: selector
  		})
	})

	try {
		return Array.from(myRows);
	} catch (err) {
		return;
	}
    }
}

/**
 * Function to filter spot when pressed the search button on filter
 * This function trigger the search, also triggered by timer
 */
function mySearch(event) {

	event.preventDefault();
	myTimer(); //force the call of query 

}

/**
* Function for construct query string for single value selection
*
* @param id {string} The html identifier used for filter
* @param param {string}the parameter for the query
* @param len {number} The maximum number of element that could be selected; use -1 if the filter permits a single selection
* @param qrystr  {string} Th initial query string to be completed with the new filter
*/
function getFilter(id,param,len,qrystr) {

	selectedFilter = [].map.call(document.getElementById(id).selectedOptions, option => option.value);
	var qryFilter ='';
	if (selectedFilter.length < len || len == -1) {
		qryFilter = selectedFilter.map(function(el) {
			if (el) {
	    		return param+'='+ el;
			} else {
				return '';
			}
		}).join('&');
		qrystr=qrystr.concat('&'.concat(qryFilter));
       if (qrystr.substring(0,1) == '&') {
    		qrystr=qrystr.substring(1)
	   }
	}
    
    return qrystr;
}

/**
 * Search / Filter cluster spot based on filter settings            
 * Gets the filter values, constructs the query parameter and 
 * make the request to the server
 */
function myTimer() {
	var request = new XMLHttpRequest()
	var qryAll='';

    qryAll=getFilter('band','b',14,qryAll);
    qryAll=getFilter('de_re','e',7,qryAll);
    qryAll=getFilter('dx_re','x',7,qryAll);
    qryAll=getFilter('mode','m',3,qryAll);
	qryAll=getFilter('cqdeInput','qe',-1,qryAll);
	qryAll=getFilter('cqdxInput','qx',-1,qryAll);

	// Open a new connection, using the GET request on the URL endpoint
	var qryString='spotlist';
	if (qryAll){
		qryString=qryString.concat('?'.concat(qryAll));
	}

	request.open('GET', qryString, true)
	//when received data, constructs the tables
	request.onload = function(){
		try {
			rows_list=buildHtmlTable('#bodyspot',JSON.parse(this.response),rows_list);
		} catch (err) {
			console.log(err);
			console.log(err.stack);
		}
	}
	request.send()
}
