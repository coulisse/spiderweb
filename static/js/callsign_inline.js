/* 
 * script loaded inline page in order to prepare data
 * for next operations
 */
var my_countries=jQuery.parseJSON(my_countries_json);
var my_adxo_events=jQuery.parseJSON(my_adxo_events_json);
var rows_list = new Array();
rows_list=buildHtmlTable('#bodyspot',payload_json, rows_list, my_countries.country_codes,my_callsign);
