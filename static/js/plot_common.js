
/**
* Create a cookie
*
* @param {String} cname  cookie name
* @param {string} cvalue cookie value
* @param {integer} exdays the number of the days for cookie expiration
*/      
function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/" + ";Samesite=Strict;Secure=True";
};

/**
* get a cookie 
*
* @param {String} cname  cookie name
* @returns {string} cookie value
*/    
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}


/**
* format the data refresh string for exhibit on charts
*
* @param {String} date date of the last refresh
* @returns {string} string formatted
*/  
function get_last_refresh(data){
  var dt_refresh = new Date(0); // The 0 there is the key, which sets the date to the epoch
  var dt_refresh;
  dt_refresh.setUTCSeconds(data["last_refresh"]);
  const pad = (n,s=2) => (`${new Array(s).fill(0)}${n}`).slice(-s);
  var hours = pad (dt_refresh.getHours());
  var minutes = pad(dt_refresh.getMinutes());
  var months_names = get_months_names();
  var month = months_names[dt_refresh.getMonth()];
  var day = dt_refresh.getDate();
  var year = dt_refresh.getFullYear();
  var last_refresh = "Data refresh: "+day+" of "+month+" "+year+" at "+hours+":"+minutes;
  return last_refresh;
}



/**
* format the data refresh string for exhibit on charts
*
* @returns {Array} list of months as short names
*/  
function get_months_names() {
  var months_name=[];
  for (let monthNumber = 1; monthNumber < 13; monthNumber++) {
    const date = new Date();
    date.setMonth(monthNumber - 1);
    months_name.push(date.toLocaleString('en-US', { month: 'short' }));
  };
  return months_name;
}  

/**
* format the data refresh string for exhibit on charts
*
* @param {Integer} num Number to be formatted 
* @returns {string} Number formatted with K for thousands and M for millions
*/  
function format_u_k_m(num) {
  let label;
  let sign=1;
  if (num<0){
    sign=-1;
  }
  let abs_num=Math.abs(num);
  if (abs_num==0) {
    label=abs_num
  } else {
    if (abs_num>0 && abs_num <1000) {
      label=abs_num*sign;
    } else {
      if (abs_num>=1000  && abs_num < 1000000) {
        label=abs_num/1000*sign+"K";
      } else {
        if (abs_num>=1000000) {
          label=abs_num/1000000*sign+"M";
        }
      } 
    }
  }
  return label;
}

/*
function doRefresh(){

  var chartDom = document.getElementById('chart-dx_spots_trend');
  var myChart = echarts.init(chartDom);
  plot_dst.refresh(myChart,'/plot_get_dx_spots_trend');
  
}; 

setInterval(function(){doRefresh()}, 5000);

*/