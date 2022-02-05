/* 
 * script loaded inline page in order to prepare data
 * for next operations
 */
var my_adxo_events=jQuery.parseJSON(my_adxo_events_json);
var rows_list = new Array();
buildHtmlTable('#bodyspot',payload_json, rows_list, my_callsign);
