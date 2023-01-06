/********************************************************************************
 * javascript used to build band_activity chart       
 * ******************************************************************************/
class band_activity {

    /**
     * refresh and populate chart 
     *
     * @param {String} my_cart  The HTML id where place chart
     * @param {string} end_point  This is backend end-point for chart datas
     * @param {string} region  This is the continent name (EU,AF,NA...) of the selected
     * @param {Json} bands The frequency band list (160, 80, 60... UHF, SHF)
     * @param {Json} continents  The continent list( EU, SA, ...)
     */
    refresh(my_chart, end_point, region, bands, continents){
        // Asynchronous Data Loading
            fetch(end_point+'?continent='+region)
              .then((response) => response.json())        
              .then((data) => {
            // Fill in the data
            var last_refresh=get_last_refresh(data);
            var dataMap=Array.from(data["band activity"]).map(function (item) {
                return [item[1], item[0], item[2] || '-'];
                });
            //options
            my_chart.setOption({
                tooltip: {
                    position: 'top',
                    formatter: function (p) {
                        var format =  p.seriesName  +' on ' + p.name +' band: '+'<strong>'+p.data[2]+'</strong>';
                        return format;
                    }                    
                },
                title: {
					text:"Band activity",
                    subtext: last_refresh,
                    top: 'top',
                    left:'left'
                  },   
                  toolbox: {
                    show: true,
                    showTitle: false,
                    orient: 'vertical',
                    right: 'right',
                    top : 'bottom',
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
                    data: bands,
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
                    data: continents,
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
                    inRange : {   
                        color: ['#ffffe6','yellow','red']
                        
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
    };

    /**
    * Chart creator
    *
    * @constructor
    * @param {String} chart_id The HTML id where place chart
    * @param {string} end_point This is backend end-point for chart datas
    * @param {Json} cont_cq  The continent list( EU, SA, ...)
    * @param {Json} band_freq The frequency band list (160, 80, 60... UHF, SHF)
    */    
    constructor(chart_id, end_point, cont_cq, band_freq) { 
        // Initialize the echarts instance based on the prepared dom
        var chartDom = document.getElementById(chart_id);
        var myChart = echarts.init(chartDom);

        //populate continents array
        var continents=[];
        cont_cq.forEach(function myFunction(item, index) {
            continents[index]=item['id']
        });

        //populate bands array
        var bands=[];
        band_freq.forEach(function myFunction(item, index) {
            bands[index]=item['id']
        });

        //managing region
        var selectedContinent=getCookie("user_region");
        var selectedContinent_desc=getCookie("user_region_desc");
        if (!selectedContinent) {
            selectedContinent="EU";
            selectedContinent_desc="Europe";
            setCookie("user_region",selectedContinent,60);
            setCookie("user_region_desc",selectedContinent_desc,60);
        };

        selectElement('continentInput', selectedContinent);
        
        addEventHandler(document.getElementById('continentInput'), 'change', function() {
           selectedContinent=this.value;
           selectedContinent_desc=this.options[this.selectedIndex].text;
           setCookie("user_region",selectedContinent,60);
           setCookie("user_region_desc",selectedContinent_desc,60);
           plot_ba.refresh(myChart, end_point, selectedContinent,bands,continents);
           setText('txt_continent','\xa0 Based on DX SPOTS from stations in '+ selectedContinent_desc +' during the last 15 minutes, displayed by Continent and Band');            
        });

        setText('txt_continent','\xa0 Based on DX SPOTS from stations in '+ selectedContinent_desc +' during the last 15 minutes, displayed by Continent and Band');            

        this.refresh(myChart, end_point, selectedContinent,bands,continents);

        /* resize chart*/
        var chart  = echarts.init(document.querySelector("#"+chart_id), null);
        window.addEventListener('resize',function(){
            chart.resize();
        })
    }
}

//create object
let plot_ba = new band_activity ('chart-band_activity','/plot_get_heatmap_data',continents_cq,band_frequencies);

/*setInterval(function(){doRefresh('chart-band_activity','/plot_get_heatmap_data')}, 5000);

function doRefresh(chart_id,end_point){
    var chartDom = document.getElementById(chart_id);
    var myChart = echarts.init(chartDom);
    plot_dst.refresh(myChart,end_point);   
}; 
  
*/

