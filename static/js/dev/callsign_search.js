/**
 * Receive a callsign by the html form and make the request to server
 */
function myCallsignSearch(event) {
	event.preventDefault();

	var callsign=document.getElementById('callsignInput').value;

	//replacing space and tab in callsign and set location href to the specific page
	if (callsign.replace(/\s/g, '').length > 0) {
		location.href = ('/callsign.html?c=').concat((callsign.trim()).toUpperCase());
	}
}

document.getElementById('form-callsign').addEventListener('submit', myCallsignSearch);  
