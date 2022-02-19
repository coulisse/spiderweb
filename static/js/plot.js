/**
 * Build the html plots           
 *
 * @param selector {string} The html identifier where put the plots           
 * @param data {array} List of the plots to show                              
 */
function buildHtmlPlots(selector,data) {
	$(selector).empty();

	//bands activity
	var contBandsActivity$=$('<div class="container justify-content-center"/>');
	contBandsActivity$.append($('<h3  class="text-center"/>').html('Band Activity'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_AF']+'.png" alt="propagation heatmap AF" srcset="/static/plots/'+data['propagation_heatmaps_AF']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_AN']+'.png" alt="propagation heatmap AN" srcset="/static/plots/'+data['propagation_heatmaps_AN']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_AS']+'.png" alt="propagation heatmap AS" srcset="/static/plots/'+data['propagation_heatmaps_AS']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_EU']+'.png" alt="propagation heatmap EU" srcset="/static/plots/'+data['propagation_heatmaps_EU']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_NA']+'.png" alt="propagation heatmap NA" srcset="/static/plots/'+data['propagation_heatmaps_NA']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_OC']+'.png" alt="propagation heatmap OC" srcset="/static/plots/'+data['propagation_heatmaps_OC']+'.svg">'));
	contBandsActivity$.append($('<img class="img-fluid" src="/static/plots/'+data['propagation_heatmaps_SA']+'.png" alt="propagation heatmap SA" srcset="/static/plots/'+data['propagation_heatmaps_SA']+'.svg">'));
	$(selector).append(contBandsActivity$);

	//qso per months
	$(selector).append($('<hr>'));
	var contQSO$=$('<div class="container justify-content-center"/>');
	contQSO$.append($('<img class="img-fluid" src="/static/plots/'+data['qso_months']+'.png" alt="Qso per months" srcset="/static/plots/'+data['qso_months']+'.svg">'));
	$(selector).append(contQSO$);
	
	//qso per bands and hour in last month
	contQSO$.append($('<img class="img-fluid" src="/static/plots/'+data['qso_hour_band']+'.png" alt="Qso per hour/band"  srcset="/static/plots/'+data['qso_hour_band']+'.svg">'));
	$(selector).append(contQSO$);

	//qso in the world  and hour in last month
	contQSO$.append($('<img class="img-fluid" src="/static/plots/'+data['qso_world_map']+'.png" alt="Qso per hour/band"  srcset="/static/plots/'+data['qso_world_map']+'.svg">'));
	$(selector).append(contQSO$);

	//qso trend
	contQSO$.append($('<img class="img-fluid" src="/static/plots/'+data['qso_trend']+'.png" alt="Qso trend"  srcset="/static/plots/'+data['qso_trend']+'.svg">'));
	$(selector).append(contQSO$);


}

/**
 * Timer for refresh the plot page 
 */
function plotsTimer() {
	var request = new XMLHttpRequest()
	request.open('GET','plotlist',true)
	request.onload = function(){
		try {
			buildHtmlPlots('#plotlist',JSON.parse(this.response));
		} catch (err) {
			console.log(err);
			console.log(err.stack);
		}
	}
	request.send()
}
/* 
 * script loaded inline page in order to prepare data
 * for next operations
 */
buildHtmlPlots('#plotlist',payload_json);
setInterval(plotsTimer, timer_interval_json);   
