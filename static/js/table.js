/********************************************************************************
 * javascript used to popolate main  table with spots            
 * ******************************************************************************/
var adxo_url = 'https://www.ng3k.com/misc/adxo.html'
var qrz_url = 'https://www.qrz.com/db/'

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
 * @param rl {json} Row List
 * @param callsign {string} An optional parameter with the callsign to search
 */
function buildHtmlTable(selector, data, rl, callsign) {

    if (data != null) {

        var myRows = new Array();

        //get current date
        var d = new Date();
        var dd_current = '00' + d.getUTCDate();
        dd_current = dd_current.substring(dd_current.length - 2, dd_current.length);
        var mo_current = '00' + (Number(d.getUTCMonth()) + 1);
        mo_current = mo_current.substring(mo_current.length - 2, mo_current.length);
        var yy_current = d.getUTCFullYear();
        dt_current = dd_current + '/' + mo_current + '/' + yy_current;

		//empty the table
        document.getElementById(selector).replaceChildren();

		//insert in table
        for (var i = 0; i < data.length; i++) {

            myRows[i] = data[i].rowid;

			const row = document.createElement("tr");
			row.id= data[i].rowid;
			
            var found = rl.find(element => element == data[i].rowid);
            if (callsign != undefined) {
                if (callsign == data[i].de) {
					row.id= data[i].rowid;
                } else if (callsign == data[i].dx) {
					row.id= data[i].rowid;
                }
            } else if (found == undefined && rl.length > 0) {
				row.className="table-info";
				row.id=data[i].rowid;
            }

			//Column: DE search on QRZ
			const i_qrzde = document.createElement("i");
			i_qrzde.className="bi-search";
			i_qrzde.role="button";
			i_qrzde.ariaLabel=data[i].de;
			const a_qrzde = document.createElement("a");
			a_qrzde.href=qrz_url + data[i].de;
			a_qrzde.target="_blank";
			a_qrzde.rel="noopener";
			const span_qrzde = document.createElement("span");

			//Mark DE if it found in callsign search
			const mark_qrzde = document.createElement("mark");
			mark_qrzde.textContent = textContent=data[i].de;
			if (data[i].de == callsign) {
				span_qrzde.appendChild(mark_qrzde)
			} else   {
				span_qrzde.textContent='\xa0' + data[i].de;
			}

			const td_qrzde = document.createElement("td");
			
			a_qrzde.appendChild(i_qrzde);
			td_qrzde.appendChild(a_qrzde);
			td_qrzde.appendChild(span_qrzde); 
			row.append(td_qrzde);

			//Column: frequency
            var freq = Intl.NumberFormat('it-IT', {
                style: 'decimal'
            }).format(data[i].freq);

			const span_freq = document.createElement("span");
			span_freq.className="badge bg-warning text-dark badge-responsive";
			span_freq.textContent=freq;

			const td_freq = document.createElement("td");
			td_freq.appendChild(span_freq);

			row.appendChild(td_freq);

			//Column: DX (with ADXO Management)
            var adxo = findAdxo(my_adxo_events, data[i].dx);
			var adxo_link = '<a href=' + adxo_url + ' target=_blank rel=noopener >NG3K Website</a>'
			const i_qrzdx = document.createElement("i");
			i_qrzdx.className="bi-search";
			i_qrzdx.role="button";
			i_qrzdx.ariaLabel=data[i].dx;
			const a_qrzdx = document.createElement("a");
			a_qrzdx.href=qrz_url + data[i].dx;
			a_qrzdx.target="_blank";
			a_qrzdx.rel="noopener";
			const span_qrzdx = document.createElement("span");

			//Mark DX if it found in callsign search
			const mark_qrzdx = document.createElement("mark");
			mark_qrzdx.textContent = textContent=data[i].dx;
			if (data[i].dx == callsign) {
				span_qrzdx.appendChild(mark_qrzdx)
			} else   {
				span_qrzdx.textContent='\xa0' + data[i].dx;
			}

			if (adxo != undefined) {
				const i_adxo = document.createElement("i");
				i_adxo.tabIndex=0;
				i_adxo.className="bi-megaphone-fill";
				i_adxo.style="color: cornflowerblue;";
				i_adxo.role="button";
				i_adxo.ariaLabel="dx_operations";
				i_adxo.setAttribute('data-bs-container', "body"  );
				i_adxo.setAttribute('data-bs-toggle', "popover" );
				i_adxo.setAttribute('data-bs-trigger', "focus" );
				i_adxo.setAttribute('data-bs-sanitizer', "true");
				i_adxo.setAttribute('data-bs-placement', "auto");
				i_adxo.setAttribute('data-bs-html', "true");	
				i_adxo.setAttribute('data-bs-title', "Announced DX Op.: " + adxo.summary);	
				i_adxo.setAttribute('data-bs-content', adxo.description + "data from  " + adxo_link);					
				span_qrzdx.appendChild(i_adxo);
            }

			const td_qrzdx = document.createElement("td");
			a_qrzdx.appendChild(i_qrzdx);
			td_qrzdx.appendChild(a_qrzdx);
			td_qrzdx.append(span_qrzdx); 
			row.appendChild(td_qrzdx);

			//Column: Flag
            try {
				const span_flag=document.createElement("span");
				span_flag.className="img-flag fi fi-" + data[i].iso;
				span_flag.setAttribute('data-bs-container', "body"  );
				span_flag.setAttribute('data-bs-toggle', "popover" );
				span_flag.setAttribute('data-bs-trigger', "hover" );
				span_flag.setAttribute('data-bs-placement', "left");
				span_flag.setAttribute('data-bs-content', data[i].country );

				const td_flag = document.createElement("td");
				td_flag.appendChild(span_flag);
				row.appendChild(td_flag);

            } catch (err) {
				console.log(err);
				console.log("error creating flag");
				const td_flag = document.createElement("td");
				row.appendChild(td_flag);

            }

			//Column: Country
			const td_country_code = document.createElement("td");
			td_country_code.className="d-none d-lg-table-cell d-xl-table-cell";
			td_country_code.textContent = data[i].country;
			row.appendChild(td_country_code);

			//Column: Comment			
			const td_comm = document.createElement("td");
			td_comm.className="d-none d-lg-table-cell d-xl-table-cell";
			td_comm.textContent = data[i].comm;
			row.appendChild(td_comm);

			//Column: UTC			
            var dt = new Date(data[i].time * 1000);
            var hh = '00' + dt.getUTCHours();
            hh = hh.substring(hh.length - 2, hh.length);
            var mi = '00' + dt.getMinutes();
            mi = mi.substring(mi.length - 2, mi.length);
            var dd = '00' + dt.getUTCDate();
            dd = dd.substring(dd.length - 2, dd.length);
            var mo = '00' + (Number(dt.getUTCMonth()) + 1);
            mo = mo.substring(mo.length - 2, mo.length);
            var yy = dt.getUTCFullYear();
            tm = hh + ':' + mi;
            dt = dd + '/' + mo + '/' + yy;

			const div_date_time = document.createElement("div");	
			div_date_time.className="d-flex flex-column";
			const p_time = document.createElement("div");	
			p_time.textContent=tm;
			div_date_time.appendChild(p_time);
			if (dt != dt_current) {
				const p_date = document.createElement("div");	
				p_date.textContent=dt;
				div_date_time.appendChild(p_date);
			}

			row.appendChild(div_date_time);

			//Finally append the row created to the table
            document.getElementById(selector).append(row);
        }

		  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
		  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
			return new bootstrap.Popover(popoverTriggerEl)
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
    refresh_timer(); //force the call of query 

}

/**
 * Function for construct query string for single value selection
 *
 * @param id {string} The html identifier used for filter
 * @param param {string}the parameter for the query
 * @param len {number} The maximum number of element that could be selected; use -1 if the filter permits a single selection
 * @param qrystr  {string} Th initial query string to be completed with the new filter
 */
function getFilter(id, param, len, qrystr) {

    selectedFilter = [].map.call(document.getElementById(id).selectedOptions, option => option.value);
    var qryFilter = '';
    if (selectedFilter.length < len || len == -1) {
        qryFilter = selectedFilter.map(function(el) {
            if (el) {
                return param + '=' + el;
            } else {
                return '';
            }
        }).join('&');
        qrystr = qrystr.concat('&'.concat(qryFilter));
        if (qrystr.substring(0, 1) == '&') {
            qrystr = qrystr.substring(1)
        }
    }

    return qrystr;
}

/**
 * Search / Filter cluster spot based on filter settings            
 * Gets the filter values, constructs the query parameter and 
 * make the request to the server
 */
function refresh_timer() {

    var qryAll = '';

    qryAll = getFilter('band', 'b', 14, qryAll);
    qryAll = getFilter('de_re', 'e', 7, qryAll);
    qryAll = getFilter('dx_re', 'x', 7, qryAll);
    qryAll = getFilter('mode', 'm', 3, qryAll);
    qryAll = getFilter('cqdeInput', 'qe', -1, qryAll);
    qryAll = getFilter('cqdxInput', 'qx', -1, qryAll);



    // Open a new connection, using the GET request on the URL endpoint
    var qryString = 'spotlist';
    if (qryAll) {
        qryString = qryString.concat('?'.concat(qryAll));
    }

    fetch(qryString)
        .then((response) => response.json())
        .then((data) => {
            try {
                rows_list = buildHtmlTable('bodyspot', data, rows_list);
            } catch (err) {
                console.log(err);
                console.log(err.stack);
                console.log(data);
            }
        })

}