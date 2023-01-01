/********************************************************************************
 * javascript used to build band/hour chart      
 * ******************************************************************************/

class hour_band {
    
  /**
   * refresh and populate chart 
   *
   * @param {String} my_cart  The HTML id where place chart
   * @param {string} end_point  This is backend end-point for chart datas
   * @param {Json} bands The frequency band list (160, 80, 60... UHF, SHF)
   */
  refresh(my_chart,end_point,bands) {

      // Asynchronous Data Loading

      $.getJSON(end_point).done(function(data) {
          // Fill in the dat

          var last_refresh=get_last_refresh(data);
          //set hour indicator names
          var hour_indicators=[];

          //for (let i = 0; i < 24; i++) {
          for (let i = 23; i > -1; i--) {
            var hour_name={};
            var s=i.toString();
            hour_name["name"]=s;
            hour_indicators.push(hour_name);
          }

          //cycling whithin each bands and hours
          var dataMap=[];
          bands.forEach(band_item => {
            var qso=[];
           
              //for (let i = 0; i < 24; i++) {
              for (let i = 23; i > -1; i--) {                
                try {
                  var value=data["hour_band"][band_item][i];
                  if (typeof value == 'undefined') {
                    value = 0;
                  } 
                  qso.push(value);
                } catch (TypeError) {
                  //TODO
                }
            }       
            var tot={"value":qso,"name":band_item};
            dataMap.push(tot);
          });


          //options
          my_chart.setOption({
            legend: {
  
              orient: 'horizontal',
              left: 'left',
              bottom: 'bottom'                        
            },
            title: {
              text: "DX SPOTS per hour in last month",
              subtext: last_refresh,
              top: 'top',
              right: 'right',
            },            
            tooltip: {
              trigger: "axis",
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
                    return "Band: "+params.name;
                  },                       
                },              
                emphasis: {
                  lineStyle: {
                    width: 4
                  }
                },                                
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
  * @param {Json} band_freq The frequency band list (160, 80, 60... UHF, SHF)
  */      
  constructor(chart_id,end_point,band_freq) { 
      // Initialize the echarts instance based on the prepared dom
      var chartDom = document.getElementById(chart_id);
      var myChart = echarts.init(chartDom);

      //populate bands array
      var bands=[];
      band_freq.forEach(function myFunction(item, index) {
          bands[index]=item['id']
      });

      this.refresh(myChart,end_point,bands);

      //resize
      var chart  = echarts.init(document.querySelector("#"+chart_id), null);
      window.addEventListener('resize',function(){
          chart.resize();
      }) 
  };
}

//create object
let plot_hb = new hour_band('chart-hour_band','/plot_get_hour_band',band_frequencies);
