/* 
 * script loaded inline page in order to prepare data
 * for next operations
 */
//var my_adxo_events=jQuery.parseJSON(my_adxo_events_json.replaceAll("\t",""));
var my_adxo_events = JSON.parse(my_adxo_events_json.replaceAll('\t', ''));


//var qryString = 'spotlist?c=' + callsign;
let params = {};
params['callsign']=callsign;

//let csrfToken = document.querySelector("meta[name='csrf-token']").getAttribute("content");	

fetch('spotlist', {
	method: 'POST',
	cache: 'no-cache',
	credentials: 'same-origin',
	headers: {
		'Content-Type': 'application/json'				
	},
	body: JSON.stringify( params )  
})
	.then((response) => response.json())
	.then((data) => {
		try {
			//tb.build(data, my_callsign);
			tb.build(data, callsign);
		} catch (err) {
			console.log(err);
			console.log(err.stack);
			console.log(data);
		}
	});



