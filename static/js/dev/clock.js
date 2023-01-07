function showTime(){
	let date=new Date();
	let utc = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
	let time = utc.toTimeString().split(' ')[0];
	time = time.split(':')[0]+':'+time.split(':')[1];
	document.getElementById("MyClockDisplay").innerText = time;
	document.getElementById("MyClockDisplay").textContent = time;
	setTimeout(showTime, 1000); 
}

showTime();

