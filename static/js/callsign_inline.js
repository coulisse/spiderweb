/* 
 * script loaded inline page in order to prepare data
 * for next operations
 */
//var my_adxo_events=jQuery.parseJSON(my_adxo_events_json.replaceAll("\t",""));
var my_adxo_events=JSON.parse(my_adxo_events_json.replaceAll("\t",""));
var rows_list = new Array();

var qryString = 'spotlist?c='+my_callsign;
fetch(qryString)
.then((response) => response.json())
.then((data) => {
    try {
        //rows_list = buildHtmlTable('bodyspot',data, rows_list, my_callsign);
        tb.build(data,my_callsign);
    } catch (err) {
        console.log(err);
        console.log(err.stack);
        console.log(data);
    }
})



