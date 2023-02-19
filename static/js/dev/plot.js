class plot_base {

	//refresh = function(){   
	refresh() {
	}

	/**
	* Chart creator
	*
	* @constructor
	* @param {String} chart_id The HTML id where place chart
	* @param {string} end_point This is backend end-point for chart datas 
	*/
	constructor(chart_id, end_point) {
		// Initialize the echarts instance based on the prepared dom
		let chartDom = document.getElementById(chart_id);
		this.end_point = end_point;
		this.myChart = echarts.init(chartDom);

		//resize
		let chart = echarts.init(document.querySelector('#' + chart_id), null);
		window.addEventListener('resize', function () {
			chart.resize();
		});
	}

}  //end class


/********************************************************************************
 * javascript used to build band_activity chart       
 * ******************************************************************************/
class band_activity extends plot_base {

	/**
	 * refresh and populate chart 
	 *
	 * @param {string} region  This is the continent name (EU,AF,NA...) of the selected
	 */
	//refresh = function(this.myChart, end_point, region, bands, continents){
	//refresh = function(region){        
	refresh(region) {
		super.refresh();
		console.log('refresh band_activity');
		if (typeof region !== 'undefined') {
			this.selectedContinent = region;
		}

		// Asynchronous Data Loading
		//fetch(this.end_point + '?continent=' + this.selectedContinent)
		const params = {
			continent: this.selectedContinent
		};

		fetch(this.end_point, {
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
				// Fill in the data
				var last_refresh = get_last_refresh(data);
				var dataMap = Array.from(data['band activity']).map(function (item) {
					return [item[1], item[0], item[2] || '-'];
				});
				//options
				this.myChart.setOption({
					tooltip: {
						position: 'top',
						formatter: function (p) {
							var format = p.seriesName + ' on ' + p.name + ' band: ' + '<strong>' + p.data[2] + '</strong>';
							return format;
						}
					},
					title: {
						text: 'Band activity',
						subtext: last_refresh,
						top: 'top',
						left: 'left'
					},
					toolbox: {
						show: true,
						showTitle: false,
						orient: 'vertical',
						right: 'right',
						top: 'bottom',
						feature: {
							mark: { show: true },
							dataView: { show: true, readOnly: true },
							restore: { show: true },
							saveAsImage: { show: true }
						}
					},
					grid: {
						height: '80%',
						left: 25,
						top: 50,
						right: 60,
						bottom: 0,
						show: true,
						backgroundColor: 'rgb(255, 255, 255)',
					},
					xAxis: {
						type: 'category',
						data: this.bands,
						axisTick: {
							show: true,
						},
						axisLine: {
							show: false,
						},
						splitArea: {
							show: true
						}
					},
					yAxis: {
						type: 'category',
						data: this.continents,
						axisTick: {
							show: true,
						},
						axisLine: {
							show: false,
						},
						splitArea: {
							show: true
						}
					},
					visualMap: {
						calculable: true,
						orient: 'vertical',
						right: 'right',
						top: 'center',
						min: 0,
						max: 30,
						inRange: {
							color: ['#ffffe6', 'yellow', 'red']

						}
					},
					series: [
						{
							name: 'Spots',
							type: 'heatmap',
							data: dataMap,
							label: {
								show: false
							},
							emphasis: {
								itemStyle: {
									shadowBlur: 10,
									shadowColor: 'rgba(100, 0, 0, 0.5)'
								}
							}
						}
					]
				});
			});
	}

	/**
	* Chart creator
	*
	* @constructor
	* @param {String} chart_id The HTML id where place chart
	* @param {string} end_point This is backend end-point for chart datas
	* @param {integer} refresh_time Time to refesh chart
	* @param {Json} cont_cq  The continent list( EU, SA, ...)
	* @param {Json} band_freq The frequency band list (160, 80, 60... UHF, SHF)
	*/
	constructor(chart_id, end_point, cont_cq, band_freq) {
		super(chart_id, end_point);

		//populate continents array
		let continents = [];
		cont_cq.forEach(function myFunction(item, index) {
			continents[index] = item['id'];
		});
		this.continents = continents;

		//populate bands array
		let bands = [];
		band_freq.forEach(function myFunction(item, index) {
			bands[index] = item['id'];
		});
		this.bands = bands;

		//managing region
		var selectedContinent = getCookie('user_region');
		var selectedContinent_desc = getCookie('user_region_desc');
		if (!selectedContinent) {
			selectedContinent = 'EU';
			selectedContinent_desc = 'Europe';
			setCookie('user_region', selectedContinent, 60);
			setCookie('user_region_desc', selectedContinent_desc, 60);
		}

		selectElement('continentInput', selectedContinent);

		addEventHandler(document.getElementById('continentInput'), 'change', function () {
			selectedContinent = this.value;
			selectedContinent_desc = this.options[this.selectedIndex].text;
			setCookie('user_region', selectedContinent, 60);
			setCookie('user_region_desc', selectedContinent_desc, 60);
			plot_ba.refresh(selectedContinent);
			setText('txt_continent', '\xa0 Based on DX SPOTS from stations in ' + selectedContinent_desc + ' during the last 15 minutes, displayed by Continent and Band');
		});

		setText('txt_continent', '\xa0 Based on DX SPOTS from stations in ' + selectedContinent_desc + ' during the last 15 minutes, displayed by Continent and Band');
		this.refresh(selectedContinent);

	}
}


/********************************************************************************
 * javascript used to build world dx spots live
 * ******************************************************************************/

class world_dx_spots_live extends plot_base {

	/**
   * refresh and populate chart 
   *
   */
	refresh() {
		super.refresh();
		console.log('refresh world_dx_spots_live');
		// Asynchronous Data Loading

		fetch(this.end_point, {
			method: 'POST',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json'						
			}
		})		

			.then((response) => response.json())
			.then((data) => {
				fetch('world.json')
					.then(response => response.text())
					.then(geoJson => {
						var last_refresh = get_last_refresh(data);
						var dataMap = [];
						data['world_dx_spots_live'].forEach(function myFunction(item, index) {
							//lon, lat, number of qso
							dataMap.push({ 'value': [item['lat'], item['lon'], item['count']] });
						});

						this.myChart.hideLoading();
						echarts.registerMap('WR', geoJson);

						this.myChart.setOption({

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
								formatter: function (val) {
									var out = 'Spots: <STRONG>' + val.value[2] + '</STRONG>';
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
								right: 'right',
							},
							series: [
								{
									type: 'scatter',
									coordinateSystem: 'geo',
									data: dataMap,
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
	constructor(chart_id, end_point) {
		super(chart_id, end_point);
		this.refresh();
	}

}

/********************************************************************************
 * javascript used to build band/hour chart      
 * ******************************************************************************/

class hour_band extends plot_base {

	/**
   * refresh and populate chart 
   *
   * @param {Json} bands The frequency band list (160, 80, 60... UHF, SHF)
   */
	refresh() {

		// Asynchronous Data Loading
		super.refresh();
		console.log('refresh hour_band');

		fetch(this.end_point, {
			method: 'POST',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json'						
			}
		})			
			.then((response) => response.json())
			.then((data) => {
				// Fill in the dat
				var last_refresh = get_last_refresh(data);
				//set hour indicator names
				var hour_indicators = [];

				for (let i = 23; i > -1; i--) {
					var hour_name = {};
					var s = i.toString();
					hour_name['name'] = s;
					hour_indicators.push(hour_name);
				}

				//cycling whithin each bands and hours
				var dataMap = [];
				this.bands.forEach(band_item => {
					var qso = [];

					for (let i = 23; i > -1; i--) {
						try {
							var value = data['hour_band'][band_item][i];
							if (typeof value == 'undefined') {
								value = 0;
							}
							qso.push(value);
						} catch (TypeError) {
							//TODO
						}
					}
					var tot = { 'value': qso, 'name': band_item };
					dataMap.push(tot);
				});


				//options
				this.myChart.setOption({
					legend: {

						orient: 'horizontal',
						left: 'left',
						bottom: 'bottom'
					},
					title: {
						text: 'DX SPOTS per hour in last month',
						subtext: last_refresh,
						top: 'top',
						right: 'right',
					},
					tooltip: {
						trigger: 'axis',
					},
					toolbox: {
						show: true,
						showTitle: false,
						orient: 'vertical',
						left: 'right',
						top: 'center',
						feature: {
							mark: { show: true },
							dataView: { show: true, readOnly: true },
							restore: { show: true },
							saveAsImage: { show: true }
						}
					},
					radar: {
						shape: 'circle',
						//startAngle: 285, //0 on left side                  
						startAngle: 105,  //0 on top                
						indicator: hour_indicators,
						center: ['47%', '46%'],
						axisName: {
							color: 'rgb(80,80,80)',
						},
					},
					series: [
						{
							lineStyle: {
								width: 2
							},
							type: 'radar',
							symbol: 'none',
							data: dataMap,
							tooltip: {
								trigger: 'item',
								formatter: (params) => {
									return 'Band: ' + params.name;
								},
							},
							emphasis: {
								lineStyle: {
									width: 4
								}
							},
						}
					]
				});
			});
	}


	/**
  * Chart creator
  *
  * @constructor
  * @param {String} chart_id The HTML id where place chart
  * @param {string} end_point This is backend end-point for chart datas
  * @param {Json} band_freq The frequency band list (160, 80, 60... UHF, SHF)
  */
	constructor(chart_id, end_point, band_freq) {
		// Initialize the echarts instance based on the prepared dom
		super(chart_id, end_point);

		//populate bands array
		let lcl_bands = [];
		band_freq.forEach(function myFunction(item, index) {
			lcl_bands[index] = item['id'];
		});
		this.bands = lcl_bands;
		this.refresh();

	}
}


/********************************************************************************
 * javascript used to build dx spots per month chart       
 * ******************************************************************************/

class dx_spots_per_month extends plot_base {

	/**
	 * refresh and populate chart 
	 */
	refresh() {

		console.log('refresh dx_spots_per_month');
		// Asynchronous Data Loading

		//$.getJSON(end_point).done(function(data) {
		
		fetch(this.end_point, {
			method: 'POST',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json'						
			}
		})		
			.then((response) => response.json())
			.then((data) => {
				// Fill in the data
				var last_refresh = get_last_refresh(data);
				var year_now = new Date().getFullYear();
				var year_0 = (year_now - 0).toString();
				var year_1 = (year_now - 1).toString();
				var year_2 = (year_now - 2).toString();

				var months_name = get_months_names();

				var dataMap_year_0 = [];
				var dataMap_year_1 = [];
				var dataMap_year_2 = [];
				for (let i = 1; i < 13; i++) {
					dataMap_year_0.push(data.spots_per_month[i].year_0);
					dataMap_year_1.push(data.spots_per_month[i].year_1);
					dataMap_year_2.push(data.spots_per_month[i].year_2);
				}

				//options
				this.myChart.setOption({
					tooltip: {
						trigger: 'axis',
						axisPointer: {
							type: 'shadow'
						}
					},
					title: {
						text: 'DX SPOTS per month',
						subtext: last_refresh,
						top: 'top',
						left: 'left'
					},
					legend: {
						data: [year_2, year_1, year_0],
						bottom: 'bottom'
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
							magicType: { show: true, type: ['line', 'bar', 'stack'] },
							restore: { show: true },
							saveAsImage: { show: true }
						}
					},
					xAxis: [
						{
							type: 'category',
							axisTick: { show: false },
							data: months_name
						}
					],
					yAxis: [
						{
							type: 'value',
							axisLabel: {
								formatter: (function (value) {
									return format_u_k_m(value);
								})
							}
						}
					],
					series: [
						{
							name: year_2,
							type: 'bar',
							barGap: 0,
							emphasis: {
								focus: 'series'
							},
							data: dataMap_year_2
						},
						{
							name: year_1,
							type: 'bar',
							emphasis: {
								focus: 'series'
							},
							data: dataMap_year_1

						},
						{
							name: year_0,
							type: 'bar',
							emphasis: {
								focus: 'series'
							},
							data: dataMap_year_0
						},
					]
				});
			});
	}

	/**
  * Chart creator
  *
  * @constructor
  * @param {String} chart_id The HTML id where place chart
  * @param {string} end_point This is backend end-point for chart datas
  */
	constructor(chart_id, end_point) {
		super(chart_id, end_point);
		this.refresh();
	}
}

/********************************************************************************
 * javascript used to build dx spots trend      
 * ******************************************************************************/

class dx_spots_trend extends plot_base {

	/**
	 * refresh and populate chart 
	 */
	refresh() {

		console.log('refresh dx_spots_trend');
		// Asynchronous Data Loading

		fetch(this.end_point, {
			method: 'POST',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json'						
			}
		})	
			.then((response) => response.json())
			.then((data) => {
				// Fill in the data
				var last_refresh = get_last_refresh(data);
				var dataMap = [];
				for (const [key, value] of Object.entries(data['spots_trend'])) {
					var tuple = [];
					tuple.push(key);
					tuple.push(value);
					dataMap.push(tuple);
				}
				//options
				this.myChart.setOption({
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
						left: 'left'
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
							formatter: (function (value) {
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

				});
			});
	}

	/**
	* Chart creator
	*
	* @constructor
	* @param {String} chart_id The HTML id where place chart
	* @param {string} end_point This is backend end-point for chart datas
	*/
	constructor(chart_id, end_point) {
		// Initialize the echarts instance based on the prepared dom
		super(chart_id, end_point);
		this.refresh();
	}
}

//create objects and timing

var plot_ba = new band_activity('chart-band_activity', '/plot_get_heatmap_data', continents_cq, band_frequencies);
setInterval(function () { plot_ba.refresh(); }, 5 * 60 * 1000);

var plot_wdsl = new world_dx_spots_live('chart-world_dx_spots_live', '/plot_get_world_dx_spots_live');
setInterval(function () { plot_wdsl.refresh(); }, 5 * 60 * 1000);

var plot_hb = new hour_band('chart-hour_band', '/plot_get_hour_band', band_frequencies);
setInterval(function () { plot_hb.refresh(); }, 1 * 60 * 60 * 1000);

var plot_dspm = new dx_spots_per_month('chart-dx_spots_x_month', '/plot_get_dx_spots_per_month');
setInterval(function () { plot_dspm.refresh(); }, 12 * 60 * 60 * 1000);

var plot_dst = new dx_spots_trend('chart-dx_spots_trend', '/plot_get_dx_spots_trend');
setInterval(function () { plot_dst.refresh(); }, 12 * 60 * 60 * 1000);