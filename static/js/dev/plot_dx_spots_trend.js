/********************************************************************************
 * javascript used to build dx spots trend      
 * ******************************************************************************/

class dx_spots_trend {
    
	/**
     * refresh and populate chart 
     *
     * @param {String} my_cart  The HTML id where place chart
     * @param {string} end_point  This is backend end-point for chart datas
     */
	refresh(my_chart,end_point) {

		// Asynchronous Data Loading

		//$.getJSON(end_point).done(function(data) {
		fetch(end_point)
			.then((response) => response.json())        
			.then((data) => {                 
				// Fill in the data
				var last_refresh=get_last_refresh(data);
				var dataMap=[];
				for (const [key, value] of Object.entries(data['spots_trend'])) {
					var tuple=[];
					tuple.push(key);
					tuple.push(value);
					dataMap.push(tuple);
				}          
				//options
				my_chart.setOption({
					tooltip: {
						trigger: 'axis',
						position: function (pt) {
							return [pt[0], '10%'];
						}
					},
					title: {
						text: 'DX SPOTS trend',
						subtext: last_refresh,
						top: 'top',
						left:'left'             
					},
					toolbox: {
						show: true,
						showTitle: false,
						orient: 'vertical',
						left: 'right',
						top: 'center',                
						feature: {
							dataView: { show: true, readOnly: false },
							dataZoom: {
								yAxisIndex: 'none'
							},           
							restore: {},
							magicType: { show: true, type: ['line', 'bar'] },                      
							saveAsImage: {},              
						}
					},
					xAxis: {
						type: 'time',
						boundaryGap: false
					},
					yAxis: {
						type: 'value',
						boundaryGap: [0, '10%'],
						axisLabel: {
							formatter: (function (value){
								return format_u_k_m(value);
							})
						}                
					},
					dataZoom: [
						{
							type: 'inside',
							start: 65,
							end: 100
						},
						{
							start: 0,
							end: 20
						},
					],

					series: [
						{
							name: 'Spots',
							type: 'line',
							smooth: true,
							symbol: 'none',
							itemStyle: {
								color: '#078513'
							},                  
							areaStyle: {
								color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
									{
										offset: 0,
										color: '#57fa75'       
									},
									{
										offset: 1,
										color: '#118226'                 
									}
								])
							},
							data: dataMap
						}
					]              
  
				})
			})
	}
    
	/**
    * Chart creator
    *
    * @constructor
    * @param {String} chart_id The HTML id where place chart
    * @param {string} end_point This is backend end-point for chart datas
    */        
	constructor(chart_id,end_point) { 
		// Initialize the echarts instance based on the prepared dom
		var chartDom = document.getElementById(chart_id);
		var myChart = echarts.init(chartDom);
		this.refresh(myChart,end_point);

		//resize
		var chart  = echarts.init(document.querySelector('#'+chart_id), null);
		window.addEventListener('resize',function(){
			chart.resize();
		});
	}
}

//create object
let plot_dst = new dx_spots_trend ('chart-dx_spots_trend','/plot_get_dx_spots_trend');
