/********************************************************************************
 * javascript used to build dx spots per month chart       
 * ******************************************************************************/

class dx_spots_per_month {
    
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
            var year_now = new Date().getFullYear();
            var year_0 = (year_now - 0).toString();
            var year_1 = (year_now - 1).toString();
            var year_2 = (year_now - 2).toString();

            var months_name = get_months_names();

            var dataMap_year_0=[];
            var dataMap_year_1=[];
            var dataMap_year_2=[];            
            for (let i = 1; i < 13; i++) {
                dataMap_year_0.push(data.spots_per_month[i].year_0);
                dataMap_year_1.push(data.spots_per_month[i].year_1);
                dataMap_year_2.push(data.spots_per_month[i].year_2);
            }            

            //options
            my_chart.setOption({
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                      type: 'shadow'
                    }
                  },
                  title: {
                    text: "DX SPOTS per month",
                    subtext: last_refresh,
                    top: 'top',
                    left:'left'
                  },                  
                  legend: {
                    data: [year_2, year_1, year_0],
                    bottom: "bottom"                  
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
                        formatter: (function (value){
                          return format_u_k_m(value)
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
        var chart  = echarts.init(document.querySelector("#"+chart_id), null);
        window.addEventListener('resize',function(){
            chart.resize();
        }) 
    };
}

//create object
let plot_dspm = new dx_spots_per_month ('chart-dx_spots_x_month','/plot_get_dx_spots_per_month');