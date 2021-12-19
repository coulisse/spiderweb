function showTime(){
    var date=new Date()
    var utc = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
    
    var time = utc.toTimeString().split(' ')[0];
    time = time.split(':')[0]+':'+time.split(':')[1];
    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;
    
    setTimeout(showTime, 1000);
    
}
showTime();

