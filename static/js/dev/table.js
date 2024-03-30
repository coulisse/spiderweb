class table_builder {
	/**
	 * Table builder constructor
	 * @param selector {string} The html identifier where build the spots table 
	*/
	constructor(selector) {
		this.selector = selector;
		this.current_data = [];
		this.first_time = true;
	}
	/**
	 * @return last_rowid {integer} the last rowid 
	*/
	getLastRowId() {
		let last_rowid;
		if (this.current_data == null) {
			last_rowid = 0;
		} else {
			if (this.current_data.length < 1) {
				last_rowid = 0;
			} else {
				last_rowid = this.current_data[0].rowid;
			}
		}
		return last_rowid;
	}

	resetData() {
		this.current_data = [];
	}
	/**
	 * @param line {object}  with the data of a single spot
	 * @param isnew {boolean} is the new rows indicator
	 * @param dt_current {string} current date in dd/mm/yyyy format
	 * @param callsign {string} optional callsign 
	 * @return a &lt;tr&gt; dom element
	*/
	#buildRow(line, isnew, dt_current, callsign = '') {
		const row = document.createElement('tr');

		if (callsign.length > 0) {
			/* 
			do not check new lines 
			*/
		} else if (isnew && !this.first_time) {
			row.className = 'table-info';
		}

		//Column: DE search on QRZ
		const i_qrzde = document.createElement('i');
		i_qrzde.className = 'bi-search';
		i_qrzde.role = 'button';
		i_qrzde.ariaLabel = line.de;
		const a_qrzde = document.createElement('a');
		a_qrzde.href = qrz_url + line.de;
		a_qrzde.target = '_blank';
		a_qrzde.rel = 'noopener';
		const span_qrzde = document.createElement('span');

		//Mark DE if it found in callsign search
		if (line.de == callsign) {
			const mark_qrzde = document.createElement('mark');
			mark_qrzde.textContent = line.de;
			span_qrzde.appendChild(mark_qrzde);
		} else {
			span_qrzde.textContent = '\xa0' + line.de;
		}

		const td_qrzde = document.createElement('td');

		a_qrzde.appendChild(i_qrzde);
		td_qrzde.appendChild(a_qrzde);
		td_qrzde.appendChild(span_qrzde);
		row.append(td_qrzde);

		//Column: frequency
		var freq = Intl.NumberFormat('it-IT', {
			style: 'decimal'
		}).format(line.freq);

		const span_freq = document.createElement('span');
		span_freq.className = 'badge bg-warning text-dark badge-responsive';
		span_freq.textContent = freq;

		const td_freq = document.createElement('td');
		td_freq.appendChild(span_freq);

		row.appendChild(td_freq);

		//Column: DX (with ADXO Management)
		var adxo = findAdxo(my_adxo_events, line.dx);
		var adxo_link = '<a href=' + adxo_url + ' target=_blank rel=noopener >NG3K Website</a>';
		const i_qrzdx = document.createElement('i');
		i_qrzdx.className = 'bi-search';
		i_qrzdx.role = 'button';
		i_qrzdx.ariaLabel = line.dx;
		const a_qrzdx = document.createElement('a');
		a_qrzdx.href = qrz_url + line.dx;
		a_qrzdx.target = '_blank';
		a_qrzdx.rel = 'noopener';
		const span_qrzdx = document.createElement('span');

		//Mark DX if it found in callsign search
		const mark_qrzdx = document.createElement('mark');
		mark_qrzdx.textContent = line.dx;
		if (line.dx == callsign) {
			span_qrzdx.appendChild(mark_qrzdx);
		} else {
			span_qrzdx.textContent = '\xa0' + line.dx;
		}

		if (adxo != undefined) {
			const i_adxo = document.createElement('i');
			i_adxo.tabIndex = 0;
			i_adxo.className = 'bi-megaphone-fill';
			i_adxo.style = 'color: cornflowerblue;';
			i_adxo.role = 'button';
			i_adxo.ariaLabel = 'dx_operations';
			i_adxo.setAttribute('data-bs-container', 'body');
			i_adxo.setAttribute('data-bs-toggle', 'popover');
			i_adxo.setAttribute('data-bs-trigger', 'focus');
			i_adxo.setAttribute('data-bs-sanitizer', 'true');
			i_adxo.setAttribute('data-bs-placement', 'auto');
			i_adxo.setAttribute('data-bs-html', 'true');
			i_adxo.setAttribute('data-bs-title', 'Announced DX Op.: ' + adxo.summary);
			i_adxo.setAttribute('data-bs-content', adxo.description + 'data from  ' + adxo_link);
			span_qrzdx.appendChild(i_adxo);
		}

		const td_qrzdx = document.createElement('td');
		a_qrzdx.appendChild(i_qrzdx);
		td_qrzdx.appendChild(a_qrzdx);
		td_qrzdx.append(span_qrzdx);
		row.appendChild(td_qrzdx);

		//Column: Flag
		try {
			const span_flag = document.createElement('span');
			span_flag.className = 'img-flag fi fi-' + line.iso;
			span_flag.setAttribute('data-bs-container', 'body');
			span_flag.setAttribute('data-bs-toggle', 'popover');
			span_flag.setAttribute('data-bs-trigger', 'hover');
			span_flag.setAttribute('data-bs-placement', 'left');
			span_flag.setAttribute('data-bs-content', line.country);

			const td_flag = document.createElement('td');
			td_flag.appendChild(span_flag);
			row.appendChild(td_flag);

		} catch (err) {
			console.log(err);
			console.log('error creating flag');
			const td_flag = document.createElement('td');
			row.appendChild(td_flag);
		}

		//Column: Country
		const td_country_code = document.createElement('td');
		td_country_code.className = 'd-none d-lg-table-cell d-xl-table-cell';
		td_country_code.textContent = line.country;
		row.appendChild(td_country_code);

		//Column: Comment			
		const td_comm = document.createElement('td');
		td_comm.className = 'd-none d-lg-table-cell d-xl-table-cell';
		try {
			td_comm.textContent = line.comm.substring(0, 100);
		} catch (err) {
			td_comm.textContent = '';
		}
		row.appendChild(td_comm);

		//Column: UTC			
		let dt = new Date(line.time * 1000);
		let hh = '00' + dt.getUTCHours();
		hh = hh.substring(hh.length - 2, hh.length);
		let mi = '00' + dt.getMinutes();
		mi = mi.substring(mi.length - 2, mi.length);
		let dd = '00' + dt.getUTCDate();
		dd = dd.substring(dd.length - 2, dd.length);
		let mo = '00' + (Number(dt.getUTCMonth()) + 1);
		mo = mo.substring(mo.length - 2, mo.length);
		let yy = dt.getUTCFullYear();
		let tm = hh + ':' + mi;
		dt = dd + '/' + mo + '/' + yy;

		const div_date_time = document.createElement('div');
		div_date_time.className = 'd-flex flex-column';
		const p_time = document.createElement('div');
		p_time.textContent = tm;
		div_date_time.appendChild(p_time);
		if (dt != dt_current) {
			const p_date = document.createElement('div');
			p_date.textContent = dt;
			div_date_time.appendChild(p_date);
		}

		row.appendChild(div_date_time);

		//Finally append the row created to the table
		return row;
	}

	/**
	 * Build the table with the spot
	 *
	 * @param data {json} The payload with all the spots received from cluster
	 * @param rl {json} Row List
	 * @param callsign {string} An optional parameter with the callsign to search
	 */
	build(data, callsign) {

		if (data != null) {

			//get current date
			let d = new Date();
			let dd_current = '00' + d.getUTCDate();
			dd_current = dd_current.substring(dd_current.length - 2, dd_current.length);
			let mo_current = '00' + (Number(d.getUTCMonth()) + 1);
			mo_current = mo_current.substring(mo_current.length - 2, mo_current.length);
			let yy_current = d.getUTCFullYear();
			let dt_current = dd_current + '/' + mo_current + '/' + yy_current;

			//empty the table
			document.getElementById(this.selector).replaceChildren();

			//insert in table new elements
			let merge_data = [];
			for (let i = 0; i < data.length; i++) {
				document.getElementById(this.selector).append(this.#buildRow(data[i], true, dt_current, callsign));
				merge_data.push(data[i]);
			}

			//insert in html table previous elements
			for (let i = 0; i < this.current_data.length - data.length; i++) {
				document.getElementById(this.selector).append(this.#buildRow(this.current_data[i], false, dt_current, callsign));
				merge_data.push(this.current_data[i]);
			}

			//replace current data with merge
			this.current_data = merge_data;

			var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
			var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
				return new bootstrap.Popover(popoverTriggerEl);
			});

			this.first_time = false;
		}
	}
} //end class


/********************************************************************************
 * javascript used to popolate main  table with spots            
 * ******************************************************************************/
const adxo_url = 'https://www.ng3k.com/misc/adxo.html';
const qrz_url = 'https://www.qrz.com/db/';
const tb = new table_builder('bodyspot');
var params_sv = {};

/**
 * Decode Announced Dx Operation (ng3k)
 *
 * @param adxo {adxo} This is the json containing all the dxo events
 * @param callsign_to_find {callsign_to_find} The callsign of the current dx line
 */
function findAdxo(adxo, callsign_to_find) {
	if (adxo) {
		for (let i = 0; i < adxo.length; i++) {
			if (adxo[i].callsign == callsign_to_find) {
				return adxo[i];
			}
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
 * @param len {number} The maximum number of element that could be selected; use -1 if the filter permits a single selection
 * @param qry_json {object} The input json 
 */
function compose_filter(id, len, qry_json) {

	try {
		if (len == 0) {  //checkboxes
			qry_json[id] = document.getElementById(id).checked; 
		} else {
			let selectedFilter = [].map.call(document.getElementById(id).selectedOptions, option => option.value);
			if (selectedFilter.length < len) { //lists
				qry_json[id] = [];
				selectedFilter.map(function (el) {
					if (el) {
						qry_json[id].push(el);
					} else {
						return '';
					}
				});
			} else if (len == -1) {    //combo-box
				selectedFilter.map(function (el) {
					if (el) {
						qry_json[id] = el;
					} else {
						return '';
					}
				});
			}
		}
	}
	catch (err) {
		if (err instanceof TypeError) {
			console.log(err.name + ' managed - it is ok: probabilly ther is no filter on cq region');
		} else {
			throw err;
		}
	}

	return qry_json;
}

/**
 * Search / Filter cluster spot based on filter settings            
 * Gets the filter values, constructs the query parameter and 
 * make the request to the server
 */
function refresh_timer() {

	let params = {};

	//get other filters
	params = compose_filter('dxcalls', 14, params);
	params = compose_filter('band', 14, params);
	params = compose_filter('de_re', 7, params);
	params = compose_filter('dx_re', 7, params);
	params = compose_filter('mode', 3, params);
	params = compose_filter('cqdeInput', -1, params);
	params = compose_filter('cqdxInput', -1, params);
	params = compose_filter('exclft8', 0, params);
	params = compose_filter('exclft4', 0, params);


	delete params_sv['lr'];  //remove line row number, for future param comparison	
	//If the filter is changed we need to reset the data table and restart from rowid=0
	if (JSON.stringify(params) !== JSON.stringify(params_sv)) {
		tb.resetData();
		params_sv = params;
	}
	params['lr'] = tb.getLastRowId();

	//Open a new connection, using the GET request on the URL endpoint
	//let csrfToken = document.querySelector("meta[name='csrf-token']").getAttribute("content");	
	fetch('spotlist', {
		method: 'POST',
		cache: 'no-cache',
		credentials: 'same-origin',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(params)
	})
		.then((response) => response.json())
		.then((data_new) => {
			try {
				tb.build(data_new);
			} catch (err) {
				console.log(err);
				console.log(err.stack);
				console.log(data_new);
			}
		});
}


