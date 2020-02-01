$(document).ready(function(){
    //connect to the socket server.
console.log("prova");
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var numbers_received = [];

    //receive details from server
    socket.on('telnetout', function(msg) {
        console.log("Received number" + msg.telnet_output);
        //maintain a list of ten numbers
        if (numbers_received.length >= 10){
            numbers_received.shift()
        }            
        numbers_received.push(msg.telnet_output);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });

});
