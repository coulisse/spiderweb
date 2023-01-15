/********************************************************************************
 * javascript used to build world dx spots live
 * ******************************************************************************/

class world_dx_spots_live {
    
	/**
   * refresh and populate chart 
   *
   * @param {String} my_cart  The HTML id where place chart
   * @param {string} end_point  This is backend end-point for chart datas
   */
	refresh(my_chart,end_point) {

		// Asynchronous Data Loading
		fetch(end_point)
			.then((response) => response.json())        
			.then((data) => {  
				fetch('world.json')
					.then(response => response.text())
					.then(geoJson => {
						var last_refresh=get_last_refresh(data);
						var dataMap=[];
						data['world_dx_spots_live'].forEach(function myFunction(item, index) {
							//lon, lat, number of qso
							dataMap.push({'value':[item['lat'],item['lon'],item['count']]});              
						});

						my_chart.hideLoading();
						echarts.registerMap('WR', geoJson);      
            
						my_chart.setOption( {

							visualMap: {
								show: false,
								min: 0,
								max: 30,
								inRange: {
									symbolSize: [5, 20]
								}            
							},

							geo: {
								type: 'map',
								map: 'WR',
								roam: true,
								zoom: 1.2,
								aspectScale: 1,
								layoutCenter: ['50%', '54%'],
								layoutSize: '100%',
								itemStyle: {
									normal: {
										areaColor: '#91cc75',
										borderColor: '#111'
									},
									emphasis: {
										areaColor: '#3ba272' //3ba272 91cc75
									}                  
								},
								label: {
									emphasis: {
										show: false
									}
								},                
							},
							tooltip: {
								trigger: 'item',
								formatter: function(val) {
									var out='Spots: <STRONG>'+ val.value[2] +'</STRONG>';
									return out;
								}
  
							},
          
							toolbox: {
								show: true,
								showTitle: false,
								orient: 'vertical',
								left: 'right',
								top: 'center',         
								feature: {
									mark: { show: true },
									dataView: { show: true, readOnly: false },
									restore: { show: true },
									saveAsImage: { show: true }
								}
							},               
							legend: {
								show: false
							},
							title: {
								text: 'World DX SPOTS in last hour',
								subtext: last_refresh,
								top: 'top',
								right:'right',
							},                               
							series: [ 
								{
									type: 'scatter', 
									coordinateSystem: 'geo', 
									data:dataMap,
									label: {
										emphasis: {
											position: 'right',
											show: false
										}
									},
									itemStyle: {
										normal: {
											color: '#fc8452',
											borderColor: '#fa0a0a',
										}
									},     
									/*                              
                  symbolSize: function (val) {
                    return val[2] / 4;
                  },
                  */                
								}
							]        
          
						});  //end options

					}          
					);         
			});      
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
let plot_wdsl = new world_dx_spots_live ('chart-world_dx_spots_live','/plot_get_world_dx_spots_live');
