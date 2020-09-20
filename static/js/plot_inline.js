/* 
 * script loaded inline page in order to prepare data
 * for next operations
 */
plot_list = buildHtmlPlots('#plotlist',payload_json);
var myPlotRefresh = setInterval(plotsTimer, timer_interval_json);   
