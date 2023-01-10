/**
 * Receive a callsign by the html form and make the request to server
 */
function myCallsignSearch() {

	callsign=document.getElementById('callsignInput').value;

	//construct query parameters
	if (callsign.replace(/\s/g, '').length > 0) {
		location.href = ('/callsign.html?c=').concat((callsign.trim()).toUpperCase());
		console.log(location.href);
		//form.action="index.html";
	}
	
}

//var frm_callsign = document.getElementById('btn-callsign-search').formAction;
//document.getElementById('btn-callsign-search').addEventListener('click',myCallsignSearch());
//document.getElementById('btn-callsign-search').addEventListener('submit',myCallsignSearch());

/*
const form_callsign = document.getElementById('form-callsign');
form_callsign.addEventListener('submit',myCallsignSearch());
*/


const btn_callsign = document.getElementById('btn-callsign-search');
btn_callsign.formAction='javascript:myCallsignSearch()';


/*
btn_callsign.formAction = 'javascript:myCallsignSearch()'; 
*/
