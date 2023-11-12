/**
 * Receive a callsign by the html form and make the request to server
 */
function myCallsignSearch(event) {
	event.preventDefault();

	var callsign=document.getElementById('callsignInput').value;

	//construct query parameters
	//replacing space and tab in callsign and set location href to the specific page
	if (callsign.replace(/\s/g, '').length > 0) {
		location.href = ('/callsign.html?c=').concat((callsign.trim()).toUpperCase());
		//form.action="index.html";
	}
}

document.getElementById('form-callsign').addEventListener('submit', myCallsignSearch);  
