/*
 script used to acquire user consent to cookie banner (and set the cookie consent)
*/
let cookie_modal = new bootstrap.Modal(document.getElementById('cookie_consent_modal'), {
	keyboard: false
});
cookie_modal.show();

//if button is pressed, setting cookie
document.getElementById('cookie_consent_btn').onclick = function(){
	setCookie('cookie_consent',true,30);
	cookie_modal.hide(); 
};
    
