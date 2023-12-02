/* 
 * script loaded inline page in order to prepare data
 * for next operations
 * Moreover, add an event to the button of the filter form
 */
//var my_adxo_events=jQuery.parseJSON(my_adxo_events_json.replaceAll("\t",""));

var my_adxo_events = JSON.parse(my_adxo_events_json.replaceAll('\t', ''));

refresh_timer(); //run first data fetch
var myRefresh = setInterval(refresh_timer, timer_interval_json);
window.onload = () => {
	document.getElementById('form-filters').addEventListener('submit', mySearch);
};

document.getElementById('MyClockDisplay').addEventListener('load', showTime());

/* managing Tom Select for selecting DX callsings */
document.addEventListener('DOMContentLoaded', function () {
	var dxcallsElement = document.getElementById('dxcalls');
	new TomSelect(document.getElementById('dxcalls'), {
		plugins: {
			remove_button: {
				title: 'Remove callsign',
			},
			'dropdown_header': {
				title: 'Callsign'
			},
			'clear_button':{
				'title':'Remove all selected options',
			}			
		},
		persist: false,
		create: true,
		createOnBlur: true,
		allowEmptyOption: true,
		maxItems: 6,
		wrap: true
	});
});


