/**
 * Receive a callsign by the html form and make the request to server
 */
function myCallsignSearch(event) {
	event.preventDefault();

	callsign=document.getElementById('callsignInput').value;

	//construct query parameters
	if (callsign.replace(/\s/g, '').length > 0) {
		location.href = ('/callsign.html?c=').concat((callsign.trim()).toUpperCase());
		console.log(location.href);
		//form.action="index.html";
	}
	
}

document.getElementById('form-callsign').addEventListener('submit', myCallsignSearch);  
