/**
 * Receive a callsign by the html form and make the request to server
 */
function myCallsignSearch(event) {
	event.preventDefault();

	var callsign = document.getElementById('callsignInput').value;

	// Callsigne sanitize
	var sanitizedCallsign = encodeURIComponent(callsign.trim().toUpperCase());
	var redirectURL = '/callsign.html?c=' + sanitizedCallsign;
	location.href = redirectURL;
}

document.getElementById('form-callsign').addEventListener('submit', myCallsignSearch);  
