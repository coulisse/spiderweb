
/* 
 * script loaded inline page in order to prepare data
 * for next operations
 * Moreover, add an event to the button of the filter form
 */
var my_adxo_events=jQuery.parseJSON(my_adxo_events_json.replaceAll("\t",""));
var rows_list = new Array();
buildHtmlTable('#bodyspot',payload_json, rows_list);
var myRefresh = setInterval(myTimer, timer_interval_json);
window.onload = () => {
	document.getElementById('form-filters').addEventListener('submit', mySearch);
};
