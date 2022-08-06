/*
 script used to acquire user conset to cookie banner (and set the cookie consent)
*/
var fn = function () {
    document.cookie = "cookie_consent=true;SameSite=Strict; Secure;max-age=2592000";
//   	document.getElementById('cookie-consent-container').hidden = true;
	$('#cookie-consent-container').modal('hide')     
};
document.getElementById('cookie-consent').onclick = fn;
$('#cookie-consent-container').modal({backdrop:"static",keyboard:false})     
$('#cookie-consent-container').modal('show')     
