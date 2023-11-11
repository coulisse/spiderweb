/**
 * Create a cookie
 *
 * @param cname {String}  cookie name
 * @param cvalue {string} cookie value
 * @param exdays {integer}  the number of the days for cookie expiration
 */
function setCookie(cname, cvalue, exdays) {
	const d = new Date();
	d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
	let expires = 'expires=' + d.toUTCString();
	if (location.protocol == 'https:') {
		document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/' + ';Samesite=Strict;Secure=True';
	} else {
		console.log('Warning: could not set secure cookie: try with Samsite Lax...');
		document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/' + ';Samesite=Lax';
	}
}

/**
* get a cookie 
*
* @param cname {String} cookie name
* @returns cookie value
*/
function getCookie(cname) {
	let name = cname + '=';
	let decodedCookie = decodeURIComponent(document.cookie);
	let ca = decodedCookie.split(';');
	for (let i = 0; i < ca.length; i++) {
		let c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return '';
}


/**
* format the data refresh string for exhibit on charts
*
* @param date {String}  date of the last refresh
* @returns string formatted
*/
function get_last_refresh(data) {
	let dt_refresh = new Date(0); // The 0 there is the key, which sets the date to the epoch
	//var dt_refresh;
	dt_refresh.setUTCSeconds(data['last_refresh']);
	const pad = (n, s = 2) => (`${new Array(s).fill(0)}${n}`).slice(-s);
	const hours = pad(dt_refresh.getHours());
	const minutes = pad(dt_refresh.getMinutes());
	const months_names = get_months_names();
	const month = months_names[dt_refresh.getMonth()];
	const day = dt_refresh.getDate();
	const year = dt_refresh.getFullYear();
	const last_refresh = 'Data refresh: ' + day + ' of ' + month + ' ' + year + ' at ' + hours + ':' + minutes;
	return last_refresh;
}

/**
* format the data refresh string for exhibit on charts
*
* @returns {Array} list of months as short names
*/
function get_months_names() {
	var months_name = [];
	for (let monthNumber = 1; monthNumber < 13; monthNumber++) {
		const date = new Date();
		date.setMonth(monthNumber - 1);
		months_name.push(date.toLocaleString('en-US', {
			month: 'short'
		}));
	}
	return months_name;
}

/**
* format the data refresh string for exhibit on charts
*
* @param {Integer} num Number to be formatted 
* @returns {string} Number formatted with K for thousands and M for millions
*/
function format_u_k_m(num) {
	let label;
	let sign = 1;
	if (num < 0) {
		sign = -1;
	}
	let abs_num = Math.abs(num);
	if (abs_num == 0) {
		label = abs_num;
	} else {
		if (abs_num > 0 && abs_num < 1000) {
			label = abs_num * sign;
		} else {
			if (abs_num >= 1000 && abs_num < 1000000) {
				label = abs_num / 1000 * sign + 'K';
			} else {
				if (abs_num >= 1000000) {
					label = abs_num / 1000000 * sign + 'M';
				}
			}
		}
	}
	return label;
}

/**
* Set a selected element of a combo box with a value
*
* @param {string} id of the selected
* @param {string} valueToSelect value to assign
*/
function selectElement(id, valueToSelect) {
	let element = document.getElementById(id);
	element.value = valueToSelect;
}

/**
* Add event Handler to element (on)
*
* @param {string} id of the element
* @param {string} eventType i.e. "change"
* @param {function} handler the function to execute whene the evenet is raised
*/
function addEventHandler(id, eventType, handler) {
	if (id.addEventListener)
		id.addEventListener(eventType, handler, false);
	else if (id.attachEvent)
		id.attachEvent('on' + eventType, handler);
}

/**
* Set a text to a specific element
*
* @param {string} id of the element
* @param {string} newvalue the value to assign to element
*/
function setText(id, newvalue) {
	var s = document.getElementById(id);
	s.innerHTML = newvalue;
}

function showTime() {
	let date = new Date();
	let utc = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
	let time = utc.toTimeString().split(' ')[0];
	time = time.split(':')[0] + ':' + time.split(':')[1];
	document.getElementById('MyClockDisplay').innerText = time;
	document.getElementById('MyClockDisplay').textContent = time;
	setTimeout(showTime, 1000);
}


document.getElementById('MyClockDisplay').addEventListener('load', showTime());
document.getElementById('copyDate').innerHTML = '2020-'.concat(new Date().getFullYear());

//Get the button for return to top page
let button_top = document.getElementById('btn-back-to-top');

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
	scrollFunction();
};

function scrollFunction() {
	if (
		document.body.scrollTop > 20 ||
		document.documentElement.scrollTop > 20
	) {
		button_top.style.display = 'block';
	} else {
		button_top.style.display = 'none';
	}
}
// When the user clicks on the button, scroll to the top of the document
//button_top.addEventListener('click', backToTop);

// When the user clicks on the button, scroll to the top of the document
button_top.addEventListener('click', backToTop);


function backToTop() {
	document.body.scrollTop = 0;
	document.documentElement.scrollTop = 0;
}
